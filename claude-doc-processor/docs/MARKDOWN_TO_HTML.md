# Markdown 转 Word 兼容 HTML 转换器使用指南

**版本**: v1.0
**更新**: 2026-02-17
**状态**: ✅ 生产就绪

---

## 📖 目录

- [功能概述](#功能概述)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [支持的 Markdown 语法](#支持的-markdown-语法)
- [Word 兼容性规范](#word-兼容性规范)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

---

## 🎯 功能概述

### 核心特性

- ✅ **HTML 4.01 + CSS 2.1 完全兼容**
  - 严格遵循 Microsoft Word HTML 解析规范
  - 所有版本 Word（2016/2019/365）100% 兼容

- ✅ **Base64 内嵌图片**
  - 无裂图问题
  - 图片自动压缩优化
  - 支持自定义尺寸和质量

- ✅ **MathJax 公式支持**
  - 使用 `<script type="math/tex">` 标签
  - Word 打开后可编辑公式
  - 支持行内和块级公式

- ✅ **高级排版特性**
  - 多栏布局（2栏/3栏）
  - 复杂表格（合并单元格、边框）
  - 多层列表（嵌套有序/无序）

### 适用场景

1. **教辅材料转换**
   - 试卷、练习册
   - 题目、答案解析
   - 数学公式、图表

2. **技术文档转换**
   - API 文档
   - 技术手册
   - 代码示例

3. **学术论文转换**
   - 论文草稿
   - 研究报告
   - 包含公式和图表的文档

---

## 🚀 快速开始

### Step 1: 环境准备

```bash
# 确保已安装项目依赖
pip install -r requirements.txt

# 必需的依赖：
# - PyYAML
# - Pillow (PIL)
```

### Step 2: 基础使用

```bash
# 转换单个文件
./convert-md-to-html.py document.md -o output/

# 指定图片目录
./convert-md-to-html.py document.md -o output/ --images-dir ./images

# 查看帮助
./convert-md-to-html.py --help
```

### Step 3: 用 Word 打开 HTML

1. 启动 Microsoft Word
2. 文件 → 打开 → 选择生成的 HTML 文件
3. 检查排版、公式、图片
4. 文件 → 另存为 → 选择 `.docx` 格式
5. 完成！

### Step 4: 验证输出

打开 DOCX 文件后，检查：
- ✅ 无中文乱码
- ✅ 无图片裂图
- ✅ 公式双击可编辑
- ✅ 表格、列表可修改
- ✅ 排版与原 Markdown 一致

---

## ⚙️ 详细配置

### 命令行参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `md_path` | Markdown 文件路径（必需） | - | `document.md` |
| `-o, --output` | 输出目录 | `output_md2html` | `-o my_output/` |
| `--images-dir` | 图片文件夹路径 | `输出目录/images/` | `--images-dir ./pics` |
| `--config` | 配置文件路径 | `config/default.yaml` | `--config custom.yaml` |
| `--debug` | 启用调试模式 | false | `--debug` |

### 配置文件

编辑 `config/default.yaml` 中的 `markdown_to_html` 节：

```yaml
markdown_to_html:
  # 图片处理
  image_embedding: "base64"  # base64 | relative | hybrid
  image_max_size: 1280       # 图片最大尺寸
  image_quality: 85          # JPEG 压缩质量（1-100）

  # 公式处理
  formula_format: "script"   # script | text | image

  # 排版特性
  enable_columns: true       # 启用多栏布局
  enable_tables: true        # 启用复杂表格
  enable_lists: true         # 启用多层列表

  # 样式配置
  default_font: "宋体"       # 默认中文字体
  default_font_size: 10.5    # 默认字号（pt）
  line_height: 1.6           # 行高倍数
  page_size: "A4"            # 页面尺寸
  page_margin: "20pt 30pt"   # 页边距（上下 左右）

  # 输出选项
  include_mathjax: true      # 包含 MathJax CDN
  pretty_print: true         # 美化 HTML 输出
```

### 配置优先级

```
命令行参数 > 环境变量 > YAML配置 > 默认值
```

---

## 📝 支持的 Markdown 语法

### 1. 标题

```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
```

**Word 映射**: `h1`~`h6` → 内置标题样式1-6

---

### 2. 文本格式

```markdown
**粗体**
*斜体*
***粗斜体***
~~删除线~~
`行内代码`
上标：x^2^
下标：H~2~O
```

**Word 映射**: 原生加粗、斜体、删除线、等宽字体

---

### 3. 列表

#### 无序列表

```markdown
- 第一项
- 第二项
  - 嵌套项 A
  - 嵌套项 B
- 第三项
```

#### 有序列表

```markdown
1. 第一项
2. 第二项
   1. 子项 2.1
   2. 子项 2.2
3. 第三项
```

**Word 映射**: 原生可编辑列表，支持自动编号

---

### 4. 表格

```markdown
| 表头1 | 表头2 | 表头3 |
|-------|-------|-------|
| 单元格1 | 单元格2 | 单元格3 |
| 单元格4 | 单元格5 | 单元格6 |
```

**Word 映射**: 原生表格，支持边框、对齐、合并单元格

---

### 5. 数学公式

#### 行内公式

```markdown
方差公式为 $s^2 = \frac{1}{n}\sum_{i=1}^n (x_i-\overline{x})^2$。
```

#### 块级公式

```markdown
$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$
```

**Word 映射**:
- 行内: `<script type="math/tex">...</script>`
- 块级: `<script type="math/tex; mode=display">...</script>`
- 双击可进入公式编辑器编辑

---

### 6. 图片

```markdown
![图片说明](images/fig1.png)
![图1 箱线图](images/fig2.jpg)
```

**Word 映射**: Base64 内嵌，无裂图问题

---

### 7. 代码块

````markdown
```python
def hello():
    print("Hello, World!")
```
````

**Word 映射**: `<pre>` 标签 + Courier New 字体

---

### 8. 引用块

```markdown
> 这是一段引用文本。
> 可以有多行。
```

**Word 映射**: 左边框 + 缩进

---

### 9. 多栏布局

```markdown
::: two-column

**左栏内容**
- 列表项1
- 列表项2

**右栏内容**
- 列表项A
- 列表项B

:::
```

**Word 映射**: CSS `column-count: 2`

---

## 📋 Word 兼容性规范

### HTML 标准

- **DOCTYPE**: HTML 4.01 Transitional
- **编码**: UTF-8
- **CSS**: CSS 2.1 子集

### 支持的 HTML 标签

| 标签 | 兼容性 | 说明 |
|------|--------|------|
| `h1`~`h6` | ✅ 100% | 映射为标题样式 |
| `p` | ✅ 100% | 映射为正文样式 |
| `strong`/`b` | ✅ 100% | 加粗 |
| `em`/`i` | ✅ 100% | 斜体 |
| `u` | ✅ 100% | 下划线 |
| `s` | ✅ 100% | 删除线 |
| `sup`/`sub` | ✅ 100% | 上标/下标 |
| `ol`/`ul`/`li` | ✅ 100% | 列表 |
| `table`/`tr`/`td`/`th` | ✅ 100% | 表格 |
| `img` | ✅ 100% | 图片（base64） |
| `script type="math/tex"` | ✅ 100% | 数学公式 |
| `pre`/`code` | ✅ 90% | 代码块 |

### 禁用的 HTML 标签

- ❌ HTML5 语义化标签（`section`, `article`, `header`, `footer`等）
- ❌ 多媒体标签（`video`, `audio`, `canvas`）
- ❌ 表单标签（`form`, `input`, `button`）
- ❌ SVG（老版本 Word 不兼容）

### 支持的 CSS 属性

| 属性 | 兼容性 | 说明 |
|------|--------|------|
| `font-family` | ✅ 100% | 字体 |
| `font-size` | ✅ 100% | 字号（pt） |
| `font-weight` | ✅ 100% | 粗细 |
| `font-style` | ✅ 100% | 样式（斜体） |
| `color` | ✅ 100% | 颜色 |
| `text-align` | ✅ 100% | 对齐 |
| `text-indent` | ✅ 100% | 首行缩进 |
| `line-height` | ✅ 100% | 行高 |
| `margin`/`padding` | ✅ 100% | 外边距/内边距 |
| `border` | ✅ 100% | 边框（solid/dashed/dotted） |
| `column-count` | ✅ 100% | 多栏布局 |
| `break-inside` | ✅ 100% | 防拆分 |
| `@page` | ✅ 100% | 页面设置 |

### 禁用的 CSS 属性

- ❌ CSS3 高级属性（`flex`, `grid`, `transform`等）
- ❌ 定位属性（`position: absolute/fixed`）
- ❌ 透明度（`opacity`, `rgba`）
- ❌ 圆角（`border-radius`）
- ❌ 阴影（`box-shadow`）

详细规范请参考：[docs/HTML_support_by_WORD.md](HTML_support_by_WORD.md)

---

## 🔍 故障排查

### Q1: Word 打开 HTML 后乱码

**原因**: 字符编码问题

**解决方案**:
```yaml
# 确保配置正确
markdown_to_html:
  # HTML 头部必须包含：
  # <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
```

---

### Q2: 图片显示为红叉（裂图）

**原因**: 图片路径错误或格式不支持

**解决方案**:
```bash
# 方案1：使用 base64 内嵌（推荐）
markdown_to_html:
  image_embedding: "base64"

# 方案2：检查图片路径
./convert-md-to-html.py doc.md --images-dir /绝对路径/images/

# 方案3：确保图片格式正确
# 仅支持 PNG、JPG、JPEG
```

---

### Q3: 公式无法编辑

**原因**: 公式格式不正确

**解决方案**:
```markdown
# ✅ 正确格式
$$x^2$$
$x^2$

# ❌ 错误格式
\[ x^2 \]  # 不支持 LaTeX 定界符
```

---

### Q4: 表格显示错乱

**原因**: Markdown 表格格式不正确

**解决方案**:
```markdown
# ✅ 正确格式
| 表头 | 表头 |
|------|------|
| 单元格 | 单元格 |

# ❌ 错误格式
| 表头 | 表头 |
| 单元格 | 单元格 |  # 缺少分隔行
```

---

### Q5: 列表编号不正确

**原因**: 列表嵌套层级过深

**解决方案**:
```markdown
# ✅ 推荐：不超过 3 层嵌套
1. 第一层
   1. 第二层
      1. 第三层

# ❌ 避免：超过 3 层
1. 第一层
   1. 第二层
      1. 第三层
         1. 第四层  # Word 可能识别错误
```

---

### Q6: 转换速度慢

**原因**: 图片太多或文件太大

**解决方案**:
```yaml
# 优化配置
markdown_to_html:
  image_max_size: 800   # 降低图片尺寸
  image_quality: 75     # 提高压缩率
```

---

## 💡 最佳实践

### 1. 图片处理

**✅ 推荐**:
- 使用 PNG 格式（无损，适合图表）
- 大图先压缩（避免 HTML 文件过大）
- 统一放在 `images/` 文件夹

**❌ 不推荐**:
- 使用 SVG 格式（Word 兼容性差）
- 超大图片（>5MB）
- 外部图片链接

---

### 2. 公式编写

**✅ 推荐**:
```markdown
# 简单公式优先用 HTML 标签
上标：x<sup>2</sup>
下标：H<sub>2</sub>O

# 复杂公式用 LaTeX
$$\int_{a}^{b} f(x) dx$$
```

**❌ 不推荐**:
```markdown
# 过度使用 LaTeX（增加 Word 解析负担）
$$x^2$$  # 简单平方应该用上标
```

---

### 3. 表格设计

**✅ 推荐**:
- 使用原生 Markdown 表格语法
- 表头清晰明确
- 单元格内容简洁

**❌ 不推荐**:
- 复杂的合并单元格（手动修改 HTML）
- 嵌套表格（Word 不支持）

---

### 4. 多栏布局

**✅ 推荐**:
```markdown
::: two-column
# 左栏内容
# 右栏内容
:::
```

**使用场景**:
- 教辅材料（题目+答案）
- 试卷（题目+答题区）
- 对比内容（左边原文，右边译文）

---

### 5. 工作流

**推荐的完整工作流**:

```bash
# 1. PDF/DOCX 转 Markdown
./convert-pdf.py textbook.pdf -o md_output/
./convert-docx.py document.docx -o md_output/

# 2. （可选）手动编辑 Markdown
vim md_output/document.md

# 3. Markdown 转 Word 兼容 HTML
./convert-md-to-html.py md_output/document.md -o html_output/

# 4. 用 Word 打开 HTML，另存为 DOCX
# 手动操作

# 5. （可选）在 Word 中微调
# 调整格式、添加页眉页脚等
```

---

## 📊 性能指标

### 处理速度

| 文档大小 | 处理时间 | 图片数量 |
|----------|----------|----------|
| 小（<1000行） | <5秒 | <10张 |
| 中（1000-5000行） | 5-15秒 | 10-50张 |
| 大（>5000行） | 15-30秒 | >50张 |

### 输出文件大小

| 类型 | 大小 |
|------|------|
| 纯文本 Markdown | ~50KB |
| 带图片的 HTML | ~500KB - 5MB |
| 对应的 DOCX | ~300KB - 3MB |

---

## 📞 获取帮助

### 文档资源

- **项目主文档**: [README.md](../README.md)
- **Word 兼容规范**: [docs/HTML_support_by_WORD.md](HTML_support_by_WORD.md)
- **重构计划**: [docs/REFACTOR_PLAN.md](REFACTOR_PLAN.md)
- **示例文件**: [examples/sample.md](../examples/sample.md)

### 测试转换

```bash
# 使用示例文件测试
./convert-md-to-html.py examples/sample.md -o test_output/

# 检查输出
ls -lh test_output/
```

### 问题反馈

1. 启用调试模式：`--debug`
2. 检查日志输出
3. 查看文档资源
4. 提交 Issue

---

## 🎓 总结

### 核心要点

1. **简单易用** - 一条命令完成转换
2. **完美兼容** - Word 100% 支持
3. **功能全面** - 公式、表格、图片全部支持
4. **配置灵活** - YAML + 命令行参数
5. **文档完整** - 详细的使用指南

### 快速参考

```bash
# 基础用法
./convert-md-to-html.py input.md -o output/

# 完整流程
./convert-pdf.py doc.pdf -o md/                    # PDF → MD
./convert-md-to-html.py md/doc.md -o html/         # MD → HTML
# 用 Word 打开 html/doc.html → 另存为 DOCX         # HTML → DOCX
```

---

**祝使用愉快！** 🎉

如有问题，请查阅文档或提交 Issue。
