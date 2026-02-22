# 微信公众号 Markdown 转换器使用指南

## 功能特性

✨ **核心功能**
- 自动将 Markdown 转换为微信公众号兼容的 HTML
- 智能列表嵌套检测（基于原始缩进）
- 跨平台字体支持（iOS/Android/Windows）
- LaTeX 公式转换为 Unicode 数学符号
- 代码块高亮和样式优化

🎨 **样式特性**
- 粗体文本：深蓝色 `rgb(15, 76, 129)`
- 删除线：浅灰色 `#999999`
- 列表符号自动处理（避免微信编辑器换行）
- 移动端优化排版

## 快速开始

### 1. 命令行使用

```bash
# 基本用法（输出到 output/<文件名>/article.html）
python scripts/convert.py article.md

# 指定输出路径
python scripts/convert.py article.md output/my_article.html
```

### 2. Python 代码调用

```python
from src.converter.wechat_markdown_converter import convert_markdown_to_wechat

# 转换 Markdown 到微信 HTML
convert_markdown_to_wechat('article.md', 'output/article.html')
```

## Markdown 语法支持

### 文本格式

```markdown
这是**粗体文本**，这是*斜体文本*，这是~~删除线文本~~。
```

### 列表

**无序列表（带嵌套）：**
```markdown
- 主项A（包含嵌套）：
  - 嵌套项目1
  - 嵌套项目2
- 主项B
```

**有序列表（自动编号）：**
```markdown
1. 第一步：
   1.1 子步骤1.1
   1.2 子步骤1.2
2. 第二步
```

**教辅题目：**
```markdown
1. 题目内容（）
   A. 选项A
   B. 选项B
   C. 选项C
   D. 选项D
```

### 数学公式

**行内公式：**
```markdown
公式：$s^2 = 1/n∑(x_i-x̅)^2$
```

**块级公式：**
```markdown
$$
∫_a^b f(x)dx = F(b) - F(a)
$$
```

### 代码块

````markdown
```python
def hello():
    print("Hello, WeChat!")
```
````

## 配置说明

### 字体配置

转换器使用跨平台字体栈，自动适配各平台：

```python
# src/converter/wechat_markdown_converter.py
FONT_FAMILY = '-apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif'
```

**各平台字体映射：**
- iOS/macOS: San Francisco / 苹方
- Windows: 微软雅黑
- Android: 思源黑体 (Noto Sans SC)

### 颜色配置

```python
# 粗体文本
BOLD_COLOR = "rgb(15, 76, 129)"  # 深蓝色

# 删除线
STRIKETHROUGH_COLOR = "#999999"  # 浅灰色

# 标题背景
HEADER_BG = "rgb(15, 76, 129)"  # 深蓝色
HEADER_TEXT = "rgb(255, 255, 255)"  # 白色
```

## 输出结构

```
output/
├── test_converter/
│   ├── article.html          # 最终 HTML 文件
│   ├── article_cover.png     # 生成的封面图（如果有）
│   └── meta.json             # 元数据
```

## 上传到微信公众号

转换后，您可以通过以下方式发布到微信公众号：

1. **手动复制**：打开 `article.html`，复制内容到微信编辑器
2. **API 上传**：使用项目的微信 API 客户端自动上传

```python
from src.wechat.api_client import WeChatApiClient

# 上传草稿
client = WeChatApiClient()
# ... (详细用法见微信 API 文档)
```

## 注意事项

⚠️ **重要提醒**

1. **列表缩进**：使用空格（2或4个）而非 Tab 来表示嵌套
   ```markdown
   ✓ 正确：
   - 主项
     - 子项
   
   ✗ 错误：
   - 主项
  	  - 子项  # 使用了Tab
   ```

2. **删除线语法**：使用双波浪线 `~~文本~~`
   ```markdown
   ~~删除的内容~~
   ```

3. **数学公式**：LaTeX 公式会自动转换为 Unicode
   - 优先使用 Unicode 数学符号
   - 复杂公式可能显示不完整

4. **图片**：建议使用微信图床或相对路径
   - 本地图片需要手动上传到微信素材库

## 故障排查

### 问题：列表没有正确嵌套

**原因**：缩进检测失败

**解决**：
- 确保使用空格而非 Tab
- 保持缩进一致（2或4个空格）

### 问题：粗体/删除线不生效

**原因**：Markdown 语法错误

**解决**：
- 粗体：`**文本**` 或 `__文本__`
- 删除线：`~~文本~~`

### 问题：公式显示异常

**原因**：LaTeX 语法不支持

**解决**：
- 检查 LaTeX 语法是否正确
- 使用支持的公式类型（基础数学符号）

## 更新日志

### v1.0 (2025-02-20)
- ✅ 基础 Markdown 到 HTML 转换
- ✅ 基于缩进的列表嵌套检测
- ✅ 跨平台字体支持
- ✅ 粗体深蓝色样式
- ✅ 删除线灰色样式
- ✅ LaTeX 公式 Unicode 转换
- ✅ 移动端优化排版

## 相关文档

- [微信 HTML/CSS 开发指南](./wechat_mp_html_css_development_guide.md)
- [项目 README](../README.md)
