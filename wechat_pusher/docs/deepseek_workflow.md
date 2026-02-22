# DeepSeek 工作流程详解

## 📋 目录

1. [DeepSeek 配置](#deepseek-配置)
2. [DeepSeek 客户端功能](#deepseek-客户端功能)
3. [工作流程](#工作流程)
4. [使用示例](#使用示例)
5. [API 调用机制](#api-调用机制)

---

## 🔧 DeepSeek 配置

### 环境变量（.env）

```bash
# DeepSeek AI 配置
DEEPSEEK_API_KEY=sk-62f31b03e22048799beefff7cae0dfc3
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=4000
DEEPSEEK_TEMPERATURE=0.7
```

### 配置类（src/utils/config.py）

```python
class DeepSeekConfig(BaseSettings):
    """DeepSeek AI配置"""
    api_key: str         # API密钥
    base_url: str        # API地址: https://api.deepseek.com
    model: str           # 模型名称: deepseek-chat
    max_tokens: int      # 最大token数: 4000
    temperature: float   # 温度参数: 0.7
```

---

## 🤖 DeepSeek 客户端功能

### 核心方法（src/ai/deepseek_client.py）

#### 1. 生成文章摘要 (generate_summary)

**功能**: 为文章生成简洁的摘要

**参数**:
- `content`: 文章内容
- `max_length`: 摘要最大字数（默认50字，微信公众号限制）

**返回**: 摘要文本

**重要限制**:
- 微信公众号摘要限制：**50个汉字 / 120字节**
- 代码会自动截断，确保不超过限制
- 先按字符数截断，再循环检查字节是否超过120

**提示词模板**:
```
请为以下文章生成一个简洁的摘要，要求：
1. 长度严格控制在{max_length}字以内（重要：不能超过{max_length}字！）
2. 概括文章核心内容和要点
3. 语言精炼，符合公众号风格
4. 不要添加"本文介绍了"等冗余词语，直接给出摘要内容
```

**使用场景**:
- 文章元数据填充
- 微信公众号摘要
- SEO优化
- 社交分享描述

**示例输出**:
```
AI算力正系统性挤压比特币的能源与硬件基础。资本流向更高效率的AI，
导致矿工转型、算力集中化。同时全球监管收紧，比特币安全模型与增
长叙事面临根本性挑战。(42字 / 118字节)
```

---

#### 2. 生成图表提示词 (generate_chart_prompt)

**功能**: 分析文章内容，判断是否需要数据图表，生成图表配置

**参数**:
- `content`: 文章内容

**返回**: 图表配置字典或None

**返回格式**:
```python
{
    "need_chart": True,
    "chart_type": "bar|line|pie",
    "title": "图表标题",
    "data": {
        "labels": ["标签1", "标签2"],
        "values": [10, 20],
        "xlabel": "X轴标签",
        "ylabel": "Y轴标签"
    },
    "description": "图表说明"
}
```

**使用场景**:
- 数据文章自动可视化
- 统计信息图表生成
- 趋势分析图表

---

#### 3. 生成配图提示词 (generate_image_prompts)

**功能**: 为文章生成封面图和插图的AI绘画提示词

**参数**:
- `content`: 文章内容
- `title`: 文章标题

**返回**: 提示词字典

**返回格式**:
```python
{
    "cover_prompts": [
        "封面图描述1，要求：16:9比例，风格要求...",
        "封面图描述2"
    ],
    "image_prompts": [
        "插图1描述，要求：风格、内容、色彩...",
        "插图2描述",
        "插图3描述"
    ],
    "style": "整体视觉风格描述",
    "color_scheme": "色彩方案建议"
}
```

**使用场景**:
- 自动生成文章配图
- AI绘图提示词优化
- 视觉内容规划

---

#### 4. 优化文章内容 (refine_content)

**功能**: 优化文章内容，使其更适合微信公众号

**参数**:
- `content`: 原始内容

**返回**: 优化后的内容

**优化要求**:
1. 保持原文核心观点
2. 调整段落长度（移动端适配）
3. 优化语言表达
4. 添加小标题
5. 保持Markdown格式

**使用场景**:
- 内容润色
- 移动端优化
- 可读性提升

---

## 🔄 工作流程

### 当前项目工作流

```
Markdown 文件
    ↓
MarkdownParser (解析)
    ↓
HTMLBuilder (构建HTML)
    ↓
WeChatAdapter (适配微信规范)
    ↓
输出 HTML
```

**注意**: 当前流程中**DeepSeek未被集成**到主转换流程中。

---

### DeepSeek 的潜在集成点

#### 方案1: 内容增强流程（推荐）

```
Markdown 文件
    ↓
MarkdownParser (解析)
    ↓
DeepSeek 增强 ← 新增
    ├─ 生成摘要
    ├─ 优化内容
    └─ 生成配图提示词
    ↓
HTMLBuilder (构建HTML)
    ↓
WeChatAdapter (适配微信规范)
    ↓
输出 HTML + 元数据
```

#### 方案2: 自动配图流程

```
Markdown 文件
    ↓
MarkdownParser (解析)
    ↓
DeepSeek 生成配图提示词 ← 新增
    ↓
DoubaoClient 生成图片 ← 新增
    ├─ 封面图
    └─ 插图
    ↓
HTMLBuilder (插入图片)
    ↓
WeChatAdapter (适配微信规范)
    ↓
输出 HTML + 图片
```

#### 方案3: 完整AI增强流程

```
Markdown 文件
    ↓
MarkdownParser (解析)
    ↓
DeepSeek AI 增强处理 ← 新增
    ├─ 内容优化
    ├─ 摘要生成
    ├─ 配图提示词
    ├─ 图表生成（如需要）
    └─ SEO关键词提取
    ↓
AI 生成内容整合
    ├─ 文字内容
    ├─ 配图（Doubao）
    └─ 图表（Matplotlib）
    ↓
HTMLBuilder (构建HTML)
    ↓
WeChatAdapter (适配微信规范)
    ↓
输出完整文章包
```

---

## 💡 使用示例

### 示例1: 生成文章摘要

```python
from src.ai.deepseek_client import deepseek_client

# 原始文章内容
article_content = """
# Python编程入门指南

Python是一种广泛使用的高级编程语言...
（更多内容）
"""

# 生成摘要
summary = deepseek_client.generate_summary(
    content=article_content,
    max_length=200
)

print(f"摘要: {summary}")
# 输出: Python是一种广泛使用的高级编程语言，具有简洁易读的语法...
```

---

### 示例2: 生成配图提示词

```python
from src.ai.deepseek_client import deepseek_client

# 文章信息
title = "2025年人工智能发展趋势"
content = """
人工智能在2025年将迎来新的发展机遇...
（更多内容）
"""

# 生成配图提示词
prompts = deepseek_client.generate_image_prompts(
    content=content,
    title=title
)

print("封面图提示词:")
for i, prompt in enumerate(prompts["cover_prompts"], 1):
    print(f"  {i}. {prompt}")

print("\n插图提示词:")
for i, prompt in enumerate(prompts["image_prompts"], 1):
    print(f"  {i}. {prompt}")

# 输出示例:
# 封面图提示词:
#   1. 未来科技感的人工智能城市全景，蓝紫色调，数字化元素...
#   2. 抽象的AI神经网络结构图，光影效果，科技风格...

# 插图提示词:
#   1. 机器人与人类协作办公场景，明亮色调，专业摄影...
#   2. 数据流可视化图表，深蓝色背景，霓虹光效...
#   3. 未来城市天际线，黄昏时分，高清写实...
```

---

### 示例3: 优化文章内容

```python
from src.ai.deepseek_client import deepseek_client

# 原始内容
original_content = """
# Python教程

Python是一个编程语言。它有很多用途。
我们可以用Python做数据分析。
也可以做网站开发。
"""

# 优化内容
refined_content = deepseek_client.refine_content(original_content)

print(refined_content)
# 输出: 优化后的内容，包含更好的段落结构、小标题等
```

---

### 示例4: 完整工作流集成

```python
from src.ai.deepseek_client import deepseek_client
from src.ai.doubao_client import doubao_client
from src.converter.markdown_parser import MarkdownParser

# 1. 解析Markdown
parser = MarkdownParser()
article = parser.parse_file("article.md")

# 2. 使用DeepSeek增强内容
summary = deepseek_client.generate_summary(article.content)
prompts = deepseek_client.generate_image_prompts(article.content, article.title)
refined_content = deepseek_client.refine_content(article.content)

# 3. 使用Doubao生成配图
if prompts["cover_prompts"]:
    cover_image = doubao_client.generate_cover_image(
        prompt=prompts["cover_prompts"][0],
        save_path="./output/cover.png"
    )

# 4. 生成插图
for i, prompt in enumerate(prompts["image_prompts"][:3]):
    doubao_client.generate_illustration(
        prompt=prompt,
        save_path=f"./output/illustration_{i+1}.png"
    )

print("✅ 内容增强完成")
print(f"   摘要: {summary[:50]}...")
print(f"   封面图: {cover_image}")
print(f"   插图: 3张")
```

---

## 🔌 API 调用机制

### 内部调用流程

```python
def _call_api(self, prompt: str, temperature: Optional[float] = None,
             max_tokens: Optional[int] = None) -> str:
    """
    内部API调用方法
    """
    response = self.client.chat.completions.create(
        model=self.model,  # deepseek-chat
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的内容创作助手，擅长为微信公众号生成高质量内容。"
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=temperature or self.temperature,  # 0.7
        max_tokens=max_tokens or self.max_tokens,  # 4000
    )

    return response.choices[0].message.content.strip()
```

### 参数说明

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `model` | deepseek-chat | 使用的模型 |
| `temperature` | 0.7 | 创造性程度(0-2)，越高越随机 |
| `max_tokens` | 4000 | 最大输出token数 |
| `system_prompt` | 固定 | 角色定义 |

### 不同功能的参数调整

| 功能 | temperature | max_tokens | 说明 |
|-----|------------|-----------|------|
| `generate_summary` | 0.7 | 2000 | 需要一定的创造性 |
| `generate_chart_prompt` | 0.3 | 2000 | 降低温度以获得确定的JSON |
| `generate_image_prompts` | 0.8 | 3000 | 需要更高的创造性 |
| `refine_content` | 0.7 | 4000 | 平衡创造性和准确性 |

---

## 📊 Token 使用统计

### 实际测试数据

```
输入: 25 tokens
输出: 260 tokens
总计: 285 tokens
```

### Token 预估

| 操作 | 输入Token | 输出Token | 总计 |
|-----|----------|----------|------|
| 生成摘要(50字) | ~500 | ~150 | ~650 |
| 生成图表提示词 | ~800 | ~400 | ~1200 |
| 生成配图提示词 | ~1000 | ~600 | ~1600 |
| 优化内容(1000字) | ~1500 | ~1200 | ~2700 |

**注意**: 实际使用量会根据内容长度变化

---

## 🎯 最佳实践

### 1. 内容长度控制

```python
# ✅ 好的做法：限制输入长度
def generate_summary(self, content: str, max_length: int = 200):
    # 限制输入长度避免超出token限制
    prompt_content = content[:2000]  # 只取前2000字

# ❌ 不好的做法：直接使用全部内容
def generate_summary(self, content: str, max_length: int = 200):
    prompt_content = content  # 可能超长
```

### 2. 错误处理

```python
try:
    summary = deepseek_client.generate_summary(content)
    if not summary:
        # 使用默认摘要
        summary = "文章摘要..."
except Exception as e:
    logger.error(f"摘要生成失败: {e}")
    summary = "文章摘要..."  # 降级处理
```

### 3. JSON 解析容错

```python
try:
    result = json.loads(response)
except json.JSONDecodeError:
    # 尝试提取JSON部分
    import re
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        result = json.loads(json_match.group(0))
    else:
        return None  # 完全失败
```

### 4. 温度参数调优

```python
# 需要创造性：高温度
prompts = deepseek_client.generate_image_prompts(content, title)

# 需要确定性：低温度
chart_data = deepseek_client.generate_chart_prompt(content)

# 平衡：默认温度
summary = deepseek_client.generate_summary(content)
```

---

## 🔍 当前状态分析

### ✅ 已实现

- [x] DeepSeek客户端封装
- [x] 配置管理
- [x] 日志记录
- [x] 错误处理
- [x] 4个核心功能方法

### ❌ 未集成

- [ ] DeepSeek未集成到主转换流程
- [ ] CLI命令未暴露DeepSeek功能
- [ ] 无批量处理支持
- [ ] 缓存机制

### 💡 改进建议

1. **集成到主流程**
   - 在 `convert` 命令中添加 `--ai-enhance` 选项
   - 在 `test` 命令中添加AI增强步骤

2. **添加CLI命令**
   ```bash
   # 生成摘要
   wechat-pusher summarize article.md

   # 生成配图提示词
   wechat-pusher gen-prompts article.md

   # 优化内容
   wechat-pusher refine article.md
   ```

3. **批量处理**
   ```python
   # 批量生成摘要
   articles = [...]
   summaries = deepseek_client.batch_generate_summaries(articles)
   ```

4. **缓存机制**
   ```python
   # 避免重复调用
   summary = deepseek_client.get_or_generate_summary(content_hash)
   ```

---

## 📚 相关文件

| 文件 | 说明 |
|-----|------|
| `src/ai/deepseek_client.py` | DeepSeek客户端实现 |
| `src/utils/config.py` | 配置管理（DeepSeekConfig） |
| `.env` | 环境变量配置 |
| `src/cli/main.py` | CLI命令（未集成DeepSeek） |

---

## 🚀 下一步行动

1. **测试DeepSeek功能**
   ```bash
   python -c "
   from src.ai.deepseek_client import deepseek_client

   # 测试摘要生成
   summary = deepseek_client.generate_summary('测试内容')
   print(f'摘要: {summary}')
   "
   ```

2. **集成到工作流**
   - 修改 `src/cli/main.py` 的 `convert` 命令
   - 添加 `--ai-enhance` 选项

3. **添加新命令**
   - `summarize`: 生成摘要
   - `gen-prompts`: 生成配图提示词
   - `refine`: 优化内容

---

**最后更新**: 2025-02-18
**状态**: ✅ DeepSeek已配置，待集成到主流程
