# Python全自动流程中Subagent调用状态说明

## 📊 当前状态总结

### ✅ 已完成
1. **创建了chart-data-researcher subagent** - 可在Claude Code CLI中使用
2. **创建了ResearchHelper包装类** - 封装了对tool_engine_local的调用
3. **集成到publisher工作流** - `_research_chart_data()`方法已更新
4. **实现了降级机制** - research不可用时自动使用默认配置

### ⚠️  当前限制
**Python全自动流程中，subagent无法直接调用**，原因：
1. Subagent是Claude Code CLI的特性，只在CLI环境有效
2. Python代码运行在独立进程中，无法访问CLI的subagent系统
3. ResearchAssistantTool需要特定依赖（cachetools）和环境配置

---

## 🔄 三种实现方式对比

### **方式1：Claude Code CLI中使用Subagent** ✅ 推荐

**使用场景**：在Claude Code中手动测试或半自动工作流

**命令**：
```bash
# 在Claude Code CLI中
Use the chart-data-researcher subagent to find data for: 折线图，显示比特币挖矿可再生能源占比（2019-2024）
```

**优点**：
- ✅ 无需额外配置
- ✅ 自动调用research_assistant
- ✅ 返回结构化JSON数据
- ✅ 可交互式调试

**缺点**：
- ❌ 需要Claude Code环境
- ❌ 不是完全自动化

**示例输出**：
```json
{
  "found": true,
  "chart_data": {
    "type": "line",
    "labels": ["2019", "2020", ...],
    "values": [74.1, 41.15, ...]
  },
  "source": "比特币矿业委员会 (BMC)"
}
```

---

### **方式2：Python代码直接调用ResearchAssistantTool** ⚠️ 需要配置

**使用场景**：完全自动化流程

**实现状态**：✅ 已集成但需要环境配置

**当前代码**：
```python
# src/utils/research_helper.py
class ResearchHelper:
    def __init__(self):
        try:
            from src.tools.research_assistant import ResearchAssistantTool
            self.ResearchAssistantTool = ResearchAssistantTool
            self.available = True
        except ImportError:
            self.available = False

    async def research_chart_data(self, description, keywords, requirements):
        research_tool = self.ResearchAssistantTool()
        result = await research_tool.search(
            keywords=keywords,
            requirements=requirements,
            detail_level="comprehensive"
        )
        return self._parse_result(result)
```

**集成点**：
```python
# src/workflow/publisher.py (行312-357)
def _research_chart_data(self, description: str):
    if not self.research_helper.is_available():
        logger.info("⚠️  research_helper不可用，使用默认配置")
        return None

    result = self.research_helper.research_chart_data_sync(
        description=description,
        keywords=self._extract_keywords(description),
        requirements=self._build_research_requirements(description)
    )

    return result
```

**优点**：
- ✅ 完全自动化
- ✅ 无需人工干预
- ✅ 已集成到工作流

**缺点**：
- ❌ 需要tool_engine_local环境
- ❌ 需要安装依赖（cachetools）
- ❌ 当前环境不可用

**启用步骤**：
```bash
# 1. 确保tool_engine_local存在
ls /home/jsjrjft/project/tool_engine_local/

# 2. 安装依赖
pip install cachetools

# 3. 测试导入
python -c "
import sys
sys.path.insert(0, '/home/jsjrjft/project/tool_engine_local')
from src.tools.research_assistant import ResearchAssistantTool
print('✅ 导入成功')
"

# 4. 运行发布流程
python -m src.cli.main publish your_article.md
```

---

### **方式3：使用默认配置** ✅ 当前默认

**使用场景**：research不可用时的降级方案

**实现**：
```python
# 当research_helper不可用时，返回None
chart_data = self._research_chart_data(description)

# _parse_chart_description会自动使用规则推断
if chart_data and chart_data.get("found"):
    # 使用真实数据
    chart_config = {...}
else:
    # 使用默认配置
    chart_config = {
        "chart_type": "line",
        "data": {
            "labels": ["2020", "2021", "2022", "2023", "2024"],
            "values": [100, 150, 200, 280, 350],
            ...
        }
    }
```

**优点**：
- ✅ 无需外部依赖
- ✅ 立即可用
- ✅ 降级机制完善

**缺点**：
- ❌ 数据不是真实的
- ❌ 仅适合测试和演示

---

## 📋 实际工作流程

### 场景1：使用Subagent（手动/半自动）

```bash
# 1. 在Claude Code中
cd /mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher

# 2. 使用subagent查找数据
Use the chart-data-researcher subagent to find data for: 折线图，显示比特币挖矿可再生能源占比（2019-2024）

# 3. 复制返回的数据

# 4. 创建文章，手动嵌入数据
cat > article.md << 'EOF'
# 比特币挖矿能源转型

[[CHART:折线图，横轴为年份（2019-2024），纵轴为占比（%），数据：2019年74.1%，2020年41.15%，2021年28.48%，2022年58.9%，2023年59.9%，2024年56.2%]]
EOF

# 5. 发布
python -m src.cli.main publish article.md
```

### 场景2：完全自动化（需要配置环境）

```bash
# 1. 配置环境
cd /home/jsjrjft/project/tool_engine_local
pip install -r requirements.txt

# 2. 回到项目
cd /mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher

# 3. 创建文章
cat > article.md << 'EOF'
# 比特币挖矿能源转型

[[CHART:折线图，横轴为年份（2019-2024），纵轴为占比（%）。显示比特币挖矿中可再生能源占比的变化趋势]]
EOF

# 4. 发布（自动调用research）
python -m src.cli.main publish article.md
```

### 场景3：使用默认配置（当前默认）

```bash
# 直接发布，系统会使用默认配置
python -m src.cli.main publish article.md
```

**日志输出**：
```
⚠️  research_helper不可用，使用默认配置
⚠️  未找到真实数据，使用默认配置
✅ 图表生成成功
```

---

## 🔍 如何判断当前可用方式

### 检查命令

```bash
# 方法1：检查ResearchHelper状态
python -c "
from src.utils.research_helper import get_research_helper
helper = get_research_helper()
print(f'ResearchHelper可用: {helper.is_available()}')
"

# 方法2：查看初始化日志
python -m src.cli.main publish article.md 2>&1 | grep -E "research_helper|图表数据"

# 方法3：运行测试
python test_chart_with_real_data.py
```

### 输出判断

**如果看到**：
```
✅ 图表数据研究助手已启用
✅ 成功找到图表数据
  来源: 比特币矿业委员会 (BMC)
```
→ **方式2可用**（直接调用ResearchAssistantTool）

**如果看到**：
```
⚠️  图表数据研究助手不可用，将使用默认配置
⚠️  未找到真实数据，使用默认配置
```
→ **使用方式3**（默认配置）

**如果在Claude Code中手动调用subagent**：
```
Use the chart-data-researcher subagent...
```
→ **方式1可用**（Subagent）

---

## 📊 当前推荐方案

### 对于开发和测试
**推荐方式3**（默认配置）
- 无需额外配置
- 立即可用
- 适合验证工作流

### 对于生产环境
**推荐方式1+2组合**：
1. 使用subagent获取数据（手动/半自动）
2. 在文章中明确指定数据
3. 使用全自动流程发布

### 示例
```bash
# 1. 使用subagent获取真实数据
Use the chart-data-researcher subagent to find data for: 比特币可再生能源占比

# 2. 在文章中使用获取的数据
cat > article.md << 'EOF'
# 比特币挖矿能源转型

[[CHART:折线图，数据：2019年74.1%，2020年41.15%，2021年28.48%，2022年58.9%，2023年59.9%，2024年56.2%]]
EOF

# 3. 全自动发布
python -m src.cli.main publish article.md
```

---

## 🎯 总结

| 方式 | 自动化程度 | 当前状态 | 适用场景 |
|------|-----------|---------|---------|
| **Subagent** | 手动/半自动 | ✅ 可用 | 开发、测试、数据获取 |
| **ResearchAssistantTool** | 完全自动 | ⚠️ 需配置 | 生产环境（需配置） |
| **默认配置** | 完全自动 | ✅ 默认 | 快速测试、演示 |

**当前推荐**：
- **快速验证**：使用默认配置（方式3）
- **获取真实数据**：使用Subagent（方式1）
- **生产部署**：配置ResearchAssistantTool（方式2）

---

## 📝 相关文件

- `.claude/agents/chart-data-researcher.md` - Subagent配置
- `src/utils/research_helper.py` - ResearchHelper包装类
- `src/workflow/publisher.py` - 集成点（行312-357）
- `test_chart_with_real_data.py` - 真实数据测试
- `docs/CHART_DATA_RESEARCH_GUIDE.md` - 使用指南
