# DeepSeek V4 工作流程详解

> **更新日期**: 2026-05-04
> **API版本**: DeepSeek V4 (2026年4月发布)

## 📋 目录

1. [DeepSeek V4 新特性](#deepseek-v4-新特性)
2. [DeepSeek 配置](#deepseek-配置)
3. [思考模式](#思考模式)
4. [客户端功能](#客户端功能)
5. [使用示例](#使用示例)

---

## 🚀 DeepSeek V4 新特性

### 模型架构更新

**新模型（2026年4月）**：
- ✅ **deepseek-v4-pro**（旗舰版）
  - 1.6T 总参数，49B 激活参数
  - 对标 GPT-4 级别性能
  - 最大上下文：1M tokens
  - 最大输出：384K tokens

- ✅ **deepseek-v4-flash**（轻量版）
  - 284B 总参数，13B 激活参数
  - 对标 GPT-4o-mini 级别
  - 极低成本，高性能日常推理
  - 相同的上下文和输出长度

**旧模型（已弃用）**：
- ⚠️ **deepseek-chat**（2026-07-24 停用）
- ⚠️ **deepseek-reasoner**（2026-07-24 停用）

### 思考模式

**重要变化**：
- ❌ **旧方式**：通过模型名区分（`deepseek-reasoner`）
- ✅ **新方式**：通过 `thinking` 参数控制
- ✅ **默认行为**：V4 模型默认开启思考模式

**思考内容隔离**：
- 思考过程自动隔离到单独字段
- `message.content` 只包含最终答案
- 不会污染响应内容

---

## 🔧 DeepSeek 配置

### 环境变量（.env）

```bash
# DeepSeek AI 配置
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro  # 或 deepseek-v4-flash
DEEPSEEK_MAX_TOKENS=4000
DEEPSEEK_TEMPERATURE=0.7
```

### 配置类（src/utils/config.py）

```python
class DeepSeekConfig(BaseSettings):
    """DeepSeek AI配置"""
    api_key: str         # API密钥
    base_url: str        # API地址: https://api.deepseek.com
    model: str           # 模型名称: deepseek-v4-pro / deepseek-v4-flash
    max_tokens: int      # 最大token数: 4000
    temperature: float   # 温度参数: 0.7
```

---

## 🧠 思考模式

### 启用思考模式

**方式1：通过 extra_body 参数（代码中）**

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[...],
    extra_body={
        "thinking": {
            "type": "enabled",
            "reasoning_effort": "high"  # 可选: "high" 或 "max"
        }
    }
)
```

**方式2：环境变量配置（推荐用于生产环境）**

```bash
# .env 文件中添加
# 启用思考模式（V4 模型默认启用）
DEEPSEEK_THINKING_ENABLED=true
DEEPSEEK_REASONING_EFFORT=high  # 可选: high, max
```

### 思考强度控制

| 参数 | 说明 | 适用场景 |
|------|------|---------|
| `"disabled"` | 禁用思考模式 | 简单任务，追求速度 |
| `"enabled"` | 启用思考模式（默认） | 日常任务，平衡速度和质量 |
| `"high"` | 高强度思考 | 复杂推理任务 |
| `"max"` | 最大强度思考 | 最复杂的分析任务 |

### 思考内容隔离

**V4 模型的响应结构**：

```python
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "最终答案（不包含思考过程）",  # ← 只有最终答案
        "reasoning_content": "思考过程..."     # ← 思考内容在单独字段（如果启用）
      }
    }
  ]
}
```

**重要**：
- ✅ `message.content` 不包含思考过程
- ✅ 思考内容自动隔离
- ✅ 无需手动提取 `<thinking>` 标签

---

## 🤖 客户端功能

### 模型分配策略

| 任务 | 使用模型 | 原因 |
|------|---------|------|
| 生成摘要 | deepseek-v4-flash | 简单任务，轻量级模型足够 |
| 生成配图提示词 | deepseek-v4-pro | 需要创意和视觉理解，保持质量 |
| 内容优化 | deepseek-v4-pro | 需要深度理解全文 |
| 图表需求分析 | deepseek-v4-pro | 结构化分析，需要强推理 |

**注意**：如果配置 `DEEPSEEK_MODEL=deepseek-v4-flash`，所有任务都将使用 flash 模型。

### 核心方法（src/ai/deepseek_client.py）

#### 1. 生成文章摘要 (generate_summary)

**功能**: 为文章生成简洁的摘要

**使用模型**: `deepseek-v4-flash`（轻量级）

**参数**:
- `content`: 文章内容
- `max_length`: 摘要最大字数（默认50字，微信公众号限制120字节）

**返回**: 摘要文本

**微信限制**：
- 摘要限制：**120字节**（中文、英文、标点都算1个字符）
- 代码会自动确保不超过限制

**提示词模板**:
```
请为以下文章生成一个简洁的摘要，要求：
1. 长度严格控制在{max_length}字以内
2. 概括文章核心洞察和关键观点
3. 语言精炼，符合"洞察、启发、不说教"的风格
4. 不要添加"本文介绍了"等冗余词语，直接给出摘要内容
```

---

#### 2. 分析图表需求 (analyze_chart_requirements)

**功能**: 分析文章是否需要生成数据图表

**使用模型**: `deepseek-v4-pro`（旗舰版）

**参数**:
- `content`: 文章内容
- `title`: 文章标题

**返回**:
```python
{
    "needs_charts": bool,  # 是否需要图表
    "requirements": [      # 图表需求列表
        {
            "description": "图表描述",
            "chart_type": "bar|line|pie",
            "position": "插入位置说明",
            "has_data": bool,
            "data_hint": "数据提示"
        }
    ]
}
```

---

#### 3. 生成配图提示词 (generate_image_prompts)

**功能**: 为文章生成封面图和插图的AI绘画提示词

**使用模型**: `deepseek-v4-pro`（旗舰版）

**参数**:
- `content`: 文章内容
- `title`: 文章标题

**返回**:
```python
{
    "cover_prompts": ["封面图描述1", "封面图描述2"],
    "image_prompts": ["插图1描述", "插图2描述", "插图3描述", "插图4描述"],
    "style": "整体视觉风格描述",
    "color_scheme": "色彩方案建议"
}
```

**风格要求**：
- 专业、克制、有质感
- 符合深度科技定位
- 避免流量化视觉元素
- **严禁文字**：图片中不要包含任何文字、标题、标签

---

#### 4. 优化文章内容 (refine_content)

**功能**: 优化文章内容，插入图片占位符

**使用模型**: `deepseek-v4-pro`（旗舰版）

**参数**:
- `content`: 原始内容
- `chart_requirements`: 图表需求列表（可选）

**返回**: 优化后的内容（包含占位符）

**占位符类型**：
- `[[IMAGE:描述]]` - 概念插图
- `[[CHART:描述]]` - 数据图表

**插入限制**：
- ⚠️ **绝对不要在正文第一个段落之前插入任何图片占位符**
- ⚠️ **封面图已经显示在文章顶部，正文开头不要再插入图片**
- ⚠️ **第一张图片必须在第一个段落内容之后插入**

---

## 💡 使用示例

### 示例1: 生成文章摘要

```python
from src.ai.deepseek_client import deepseek_client

article_content = """
# 人工智能的未来发展

人工智能正在改变我们的生活方式...
"""

summary = deepseek_client.generate_summary(article_content)
print(f"摘要: {summary}")
```

---

### 示例2: 分析图表需求

```python
chart_analysis = deepseek_client.analyze_chart_requirements(
    content=article_content,
    title="人工智能的未来发展"
)

if chart_analysis["needs_charts"]:
    print(f"需要生成 {len(chart_analysis['requirements'])} 个图表")
    for req in chart_analysis['requirements']:
        print(f"  - {req['description']} ({req['chart_type']})")
```

---

### 示例3: 完整工作流

```python
from src.ai.deepseek_client import deepseek_client
from src.workflow.publisher import article_publisher

# 发布文章（自动完成所有步骤）
success = article_publisher.publish("article.md")

# 系统会自动：
# 1. 解析 Markdown
# 2. AI 分析（摘要、封面图提示词、图表需求）
# 3. AI 优化内容（插入占位符）
# 4. 生成图片（封面图、插图）
# 5. 生成图表（如需要）
# 6. 上传素材到微信
# 7. 转换为 HTML 并嵌入图片
# 8. 发布到草稿箱
```

---

## 📊 性能说明

### Token 使用

| 操作 | 使用模型 | 输入Token | 输出Token | 说明 |
|-----|---------|----------|----------|------|
| 生成摘要(50字) | flash | ~500 | ~100 | 简单任务，轻量模型 |
| 配图提示词生成 | pro | ~1000 | ~500 | 创意任务，需要质量保证 |
| 图表需求分析 | pro | ~800 | ~300 | 结构化分析，需要强推理 |
| 内容优化(1000字) | pro | ~1500 | ~1000 | 深度理解，需要强推理 |

### 思考模式开销

- **思考模式**：会增加推理时间，但提高复杂任务质量
- **思考强度**：`max` > `high` > `enabled`
- **模型分配**：
  - **简单任务**（摘要）：自动使用 `flash` 模型，降低成本
  - **复杂任务**（配图提示词、内容优化、图表分析）：使用 `pro` 模型，确保质量
- **建议**：
  - 默认配置 `DEEPSEEK_MODEL=deepseek-v4-pro` 可获得最佳性价比
  - 如需进一步降低成本，可配置 `DEEPSEEK_MODEL=deepseek-v4-flash`（所有任务都用 flash）

---

## ⚙️ 代码实现

### 模型检测

```python
# 检测模型类型
self.is_v4_model = "deepseek-v4" in self.model
self.is_legacy_reasoner = "reasoner" in self.model

# V4 模型默认开启思考模式
if self.is_v4_model:
    request_params["extra_body"] = {
        "thinking": {
            "type": "enabled",
            "reasoning_effort": "high"
        }
    }
```

### 响应处理

```python
# V4 模型：直接返回 content（思考内容不在 content 中）
# 旧推理模型：提取 <thinking> 标签后的内容
if self.is_legacy_reasoner:
    final_content = self._extract_reasoner_content(raw_content)
else:
    return raw_content
```

---

## 📚 相关资源

- **DeepSeek API 文档**: https://api-docs.deepseek.com
- **思考模式指南**: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode
- **模型定价**: https://api-docs.deepseek.com/quick_start/pricing

---

**最后更新**: 2026-05-04
**当前版本**: v2.1
**状态**: ✅ DeepSeek V4 已集成，思考模式已启用
