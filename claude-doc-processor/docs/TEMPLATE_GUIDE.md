# 模板使用指南

**版本**：v1.0.0
**更新时间**：2024-12-15
**适用版本**：v4.0+

---

## 目录

- [快速开始](#快速开始)
- [预置模板介绍](#预置模板介绍)
- [使用模板](#使用模板)
- [自定义模板](#自定义模板)
- [模板配置详解](#模板配置详解)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```bash
# 使用学术论文模板
./convert-md-to-html.py document.md --template academic -o output/

# 使用商务报告模板
./convert-md-to-html.py document.md --template business -o output/

# 查看所有可用模板
./convert-md-to-html.py --list-templates
```

### 自动转换为DOCX

```bash
# 一键生成DOCX文件
./convert-md-to-html.py document.md --template academic --to-docx
```

---

## 预置模板介绍

### 学术论文模板（academic）

**适用场景**：毕业论文、学术期刊、研究报告、学位论文

**特点**：
- ✅ 严格的中文学术排版规范
- ✅ Times New Roman + 宋体（标准学术字体）
- ✅ 1.5倍行距，首行缩进2字符
- ✅ 标准页边距（2.54cm，符合学术要求）
- ✅ 支持公式编号、图表编号、参考文献
- ✅ 三线表样式（符合学术标准）

**样式参数**：

| 配置项 | 值 |
|--------|-----|
| 正文字号 | 12pt（小四） |
| 标题字体 | 黑体 |
| 行距 | 1.5倍 |
| 页边距 | 2.54cm（上下），3.17cm（左右） |
| 首行缩进 | 2字符 |

**使用示例**：

```bash
./convert-md-to-html.py thesis.md --template academic -o thesis_output/
```

**示例文档**：`examples/academic_paper.md`

---

### 商务报告模板（business）

**适用场景**：商业计划书、项目报告、企业文档、提案、年度报告

**特点**：
- ✅ 专业的商务配色（深蓝色主题）
- ✅ Calibri + 黑体（现代商务风格）
- ✅ 清晰的层级结构
- ✅ 表格样式突出
- ✅ 支持封面页、执行摘要
- ✅ 斑马纹表格（提高可读性）

**样式参数**：

| 配置项 | 值 |
|--------|-----|
| 正文字号 | 11pt |
| 标题颜色 | #2E5090（企业蓝） |
| 表格边框 | 蓝色（#4472C4） |
| 表头背景 | 浅蓝色（#D9E2F3） |
| 行距 | 1.4倍 |

**使用示例**：

```bash
./convert-md-to-html.py report.md --template business -o report_output/
```

**示例文档**：`examples/business_report.md`

---

### 技术文档模板（technical）

**适用场景**：技术手册、API文档、开发指南、README、技术规范

**特点**：
- ✅ 代码友好（Consolas等宽字体）
- ✅ GitHub风格配色
- ✅ 语法高亮支持
- ✅ 清晰的代码块样式
- ✅ 浅灰背景（类似GitHub）
- ✅ 特殊引用框（注意、警告、错误、提示）

**样式参数**：

| 配置项 | 值 |
|--------|-----|
| 正文字号 | 10.5pt（五号） |
| 字体 | Segoe UI |
| 代码字体 | Consolas |
| 代码背景 | #F6F8FA（GitHub灰） |
| 链接颜色 | #0366D6（GitHub蓝） |

**使用示例**：

```bash
./convert-md-to-html.py api.md --template technical -o api_docs/
```

**示例文档**：`examples/technical_doc.md`

---

## 使用模板

### 列出所有模板

```bash
./convert-md-to-html.py --list-templates
```

输出示例：

```
======================================================================
可用模板列表
======================================================================

📄 academic - 学术论文
   描述: 标准学术论文格式，Times New Roman + 宋体，严格标题层级
   版本: 1.0.0

📄 business - 商务报告
   描述: 专业商务风格，Calibri + 黑体，深蓝色主题，表格突出
   版本: 1.0.0

📄 business_modern - 现代简约商务
   描述: 2026现代风格，Inter + 思源黑体，GitHub配色，简约大方
   版本: 1.0.0

📄 business_luxury - 黑金轻奢商务
   描述: 轻奢风格，Garamond + 思源宋体，黑金配色，典雅高端
   版本: 1.0.0

📄 business_fresh - 清新薄荷绿商务
   描述: 清新风格，Poppins + 苹方，薄荷绿配色，活力明快
   版本: 1.0.0

📄 business_neutral - 中性灰调商务
   描述: 专业中性风格，Helvetica + 思源黑体，灰色调，稳重可靠
   版本: 1.0.0

📄 technical - 技术文档
   描述: 开发者友好风格，Consolas + Segoe UI，GitHub深色主题
   版本: 1.0.0

📄 tender - 投标文件
   描述: 政府采购标书格式，专业严谨，三线表，符合招标要求
   版本: 1.0.0

📄 official - 党政机关公文
   描述: 严格遵循GB/T 9704-2012国标，仿宋_GB2312，固定28磅行距
   版本: 1.0.0
```

### 应用模板转换

#### 基础用法

```bash
./convert-md-to-html.py document.md --template <模板名称> -o output/
```

#### 完整示例

```bash
# 使用学术论文模板
./convert-md-to-html.py thesis.md --template academic -o thesis_output/

# 使用商务报告模板并自动转DOCX
./convert-md-to-html.py report.md --template business --to-docx -o report_output/

# 使用技术文档模板（调试模式）
./convert-md-to-html.py api.md --template technical --debug -o api_docs/
```

### 与其他参数结合使用

```bash
# 指定自定义配置 + 模板
./convert-md-to-html.py doc.md --template academic --config custom.yaml -o output/

# 指定图片目录 + 模板
./convert-md-to-html.py doc.md --template business --images-dir ./images -o output/
```

---

## 自定义模板

### 基于现有模板修改

1. 复制现有模板作为基础：

```bash
cp config/templates/academic.yaml config/templates/my_custom.yaml
```

2. 编辑 `my_custom.yaml`，修改需要的参数

3. 使用自定义模板：

```bash
./convert-md-to-html.py doc.md --template my_custom -o output/
```

### 创建全新模板

1. 参考 `config/templates/custom_example.yaml` 创建新模板

2. 最小化模板配置示例：

```yaml
template_name: "我的模板"
template_description: "简短描述"
template_version: "1.0.0"

styles:
  fonts:
    default: "宋体"
    heading: "黑体"
  font_sizes:
    body: 12
    heading1: 18
  colors:
    text: "#000000"
    heading: "#000000"

layout:
  page_size: "A4"
  margins:
    top: "2.54cm"
    bottom: "2.54cm"
    left: "3.17cm"
    right: "3.17cm"

features:
  enable_tables: true
  enable_lists: true
```

3. 保存到 `config/templates/` 目录

---

## 模板配置详解

### 配置文件结构

```yaml
# 模板元信息
template_name: "模板名称"
template_description: "模板描述"
template_version: "1.0.0"

# 样式配置
styles:
  fonts: {...}           # 字体配置
  font_sizes: {...}      # 字号配置
  spacing: {...}         # 间距配置
  colors: {...}          # 颜色配置

# 页面布局
layout:
  page_size: "A4"
  margins: {...}
  paragraph: {...}

# 标题样式
headings:
  h1: {...}
  h2: {...}
  h3: {...}
  ...

# 表格样式
tables: {...}

# 图片样式
images: {...}

# 功能开关
features: {...}
```

### 关键配置项说明

#### 字体配置

```yaml
styles:
  fonts:
    default: "宋体"              # 中文默认字体
    western: "Times New Roman"   # 西文默认字体
    heading: "黑体"              # 标题字体
    code: "Courier New"          # 代码字体
```

**注意**：必须使用Word内置字体，否则可能导致显示问题。

常用Word内置字体：
- 中文：宋体、黑体、楷体、仿宋
- 西文：Times New Roman、Arial、Calibri
- 代码：Courier New、Consolas

#### 字号配置

```yaml
styles:
  font_sizes:
    body: 12        # 正文（pt）
    heading1: 18    # 一级标题
    heading2: 16    # 二级标题
    heading3: 14    # 三级标题
    caption: 10.5   # 图表标题
```

中文字号对照表：

| pt | 号数 | 用途 |
|----|------|------|
| 10.5 | 五号 | 正文、图注 |
| 12 | 小四 | 正文 |
| 14 | 四号 | 三级标题 |
| 16 | 小三 | 二级标题 |
| 18 | 三号 | 一级标题 |
| 22 | 小二 | 大标题 |

#### 颜色配置

```yaml
styles:
  colors:
    text: "#000000"           # 正文颜色（十六进制）
    heading: "#2E5090"        # 标题颜色
    link: "#0000FF"           # 链接颜色
    table_border: "#000000"   # 表格边框
```

#### 页面布局

```yaml
layout:
  page_size: "A4"                    # 页面尺寸
  margins:
    top: "2.54cm"                    # 上边距
    bottom: "2.54cm"                 # 下边距
    left: "3.17cm"                   # 左边距
    right: "3.17cm"                  # 右边距
  paragraph:
    first_line_indent: "2em"         # 首行缩进
    text_align: "justify"            # 对齐方式
```

**单位说明**：
- 长度单位：`cm`（厘米）、`in`（英寸）、`pt`（磅）
- 缩进单位：`em`（字符数）

---

## 常见问题

### Q1: 如何选择合适的模板？

**答**：根据文档用途选择：

- 学术论文、毕业论文 → `academic`
- 商业报告、项目提案 → `business` 或 `business_modern`
- 技术文档、API手册 → `technical`
- 政府采购标书 → `tender`
- 党政机关公文 → `official`
- 日常简单文档 → 不指定模板（使用默认模板）

### Q2: 模板中的字体可以自定义吗？

**答**：可以，但建议使用Word内置字体：

```yaml
styles:
  fonts:
    default: "你的字体名称"
```

自定义字体要求：
- ✅ Word内置字体（如宋体、黑体、Times New Roman等）
- ❌ 非系统字体可能导致显示问题

### Q3: 如何修改模板的行距？

**答**：编辑模板文件中的 `spacing` 配置：

```yaml
styles:
  spacing:
    line_height: 1.5  # 1.5倍行距
```

常用行距：
- 1.0：单倍行距
- 1.5：1.5倍行距（学术论文标准）
- 2.0：双倍行距

### Q4: 表格边框颜色可以修改吗？

**答**：可以，在 `tables` 配置中修改：

```yaml
tables:
  border_color: "#2E5090"  # 改为蓝色
```

### Q5: 如何让标题自动编号？

**答**：在 `headings` 配置中启用编号：

```yaml
headings:
  h2:
    numbering: true  # 启用自动编号
```

### Q6: 模板不生效怎么办？

**答**：检查以下几点：

1. 模板文件是否在 `config/templates/` 目录
2. 模板文件名是否正确（不带.yaml扩展名）
3. YAML语法是否正确（注意缩进）

调试命令：

```bash
./convert-md-to-html.py doc.md --template your_template --debug
```

### Q7: 可以同时使用多个模板吗？

**答**：不可以，每次只能使用一个模板。如需不同部分的样式，可以：

- 方案1：分别转换后合并
- 方案2：创建自定义模板，结合多种风格

### Q8: 模板支持哪些页面尺寸？

**答**：支持标准页面尺寸：

- `A4`：210mm × 297mm（默认）
- `Letter`：8.5in × 11in
- `Legal`：8.5in × 14in

配置示例：

```yaml
layout:
  page_size: "A4"
```

---

## 最佳实践

### 1. 模板选择建议

**学术论文**：
- 使用 `academic` 模板
- 严格遵循格式要求
- 检查公式、图表编号

**商务报告**：
- 使用 `business` 模板
- 添加封面页和执行摘要
- 使用专业配色

**技术文档**：
- 使用 `technical` 模板
- 充分利用代码高亮
- 添加API示例

### 2. 样式一致性

- ✅ 保持同一文档使用同一模板
- ✅ 标题层级不超过4级
- ✅ 表格样式统一

### 3. 性能优化

- ✅ 大文档建议分章节处理
- ✅ 图片数量控制在合理范围（<50张）
- ✅ 公式复杂度适中

### 4. 测试工作流

```bash
# 1. 测试模板效果
./convert-md-to-html.py test.md --template academic -o test/

# 2. 用Word打开HTML检查
# 3. 确认无误后批量转换
./convert-md-to-html.py *.md --template academic -o output/
```

### 5. 版本管理

- ✅ 为不同项目创建专用模板
- ✅ 使用版本号管理模板迭代
- ✅ 记录模板变更日志

---

## 附录

### A. 模板文件位置

```
claude-doc-processor/
├── config/
│   └── templates/           # 模板目录
│       ├── academic.yaml           # 学术论文模板
│       ├── business.yaml           # 商务报告模板
│       ├── business_modern.yaml    # 现代简约商务模板
│       ├── business_luxury.yaml    # 黑金轻奢商务模板
│       ├── business_fresh.yaml     # 清新薄荷绿商务模板
│       ├── business_neutral.yaml   # 中性灰调商务模板
│       ├── technical.yaml          # 技术文档模板
│       ├── tender.yaml             # 投标文件模板
│       ├── official.yaml           # 党政机关公文模板
│       └── custom_example.yaml     # 自定义示例（教程）
```

### B. 示例文档位置

```
examples/
├── academic_paper.md         # 学术论文示例
├── business_report.md        # 商务报告示例
├── business_series_demo.md   # 商务系列示例（4个模板共用）
├── technical_doc.md          # 技术文档示例
├── technical_advanced.md     # 高级技术文档示例
├── tender_document.md        # 投标文件示例
├── official_document_demo.md # 党政机关公文示例
└── sample.md                 # 通用示例
```

### C. 进一步学习

- [Markdown语法指南](https://commonmark.org/help/)
- [Word HTML兼容性规范](../docs/HTML_support_by_WORD.md)
- [API文档](../docs/MARKDOWN_TO_HTML.md)

---

**文档维护**：Claude Doc Processor Team
**反馈渠道**：[GitHub Issues](https://github.com/your-repo/issues)
**更新频率**：随版本更新

---

*最后更新：2024-12-15*
