# Claude Doc Processor - 文档处理工作区

> **定位**: AI驱动的智能文档处理工作区
> **版本**: v4.0
> **核心理念**: 命令行工具，一键处理

提供PDF/DOCX转Markdown、Markdown转Word/HTML/PDF的完整工具链，支持9种专业模板。

---

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置API密钥
```bash
export DEEPSEEK_API_KEY="your_key"
```

### 基本使用
```bash
# PDF/DOCX → Markdown
./convert.py document.pdf -o output/

# Markdown → Word
./convert-md-to-html.py document.md --template academic --to-docx
```

---

## 📖 核心工具

### 1. convert.py - 文档转换工具

**功能**: PDF/DOCX → Markdown

#### 基础用法
```bash
./convert.py <输入文件> [选项]
```

#### 常用参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `-o, --output` | 输出目录 | `-o output/` |
| `--refine-content` | 启用内容精修（高质量） | `--refine-content` |
| `--max-pages N` | 限制处理页数 | `--max-pages 10` |
| `--start-page N` | 从第N页开始 | `--start-page 51` |
| `--batch` | 批量处理模式 | `--batch` |

#### 使用示例

**单个文档转换**
```bash
# PDF → Markdown
./convert.py document.pdf -o output/

# DOCX → Markdown
./convert.py document.docx -o output/

# 高质量转换（推荐学术论文）
./convert.py paper.pdf --refine-content -o output/
```

**大文档分页处理**
```bash
# 处理前100页
./convert.py large.pdf --max-pages 100 -o part1/

# 从第51页开始处理50页
./convert.py large.pdf --start-page 51 --max-pages 50 -o part2/

# 分批处理1000页PDF（分10批，每批100页）
for i in {0..9}; do
  start=$((i*100 + 1))
  ./convert.py large.pdf --start-page $start --max-pages 100 -o part_$((i+1))/
done
```

**批量处理**
```bash
# 批量转换多个PDF
./convert.py "docs/*.pdf" --batch -o batch_output/
```

#### 输出结果
```
output/
├── document.md          # Markdown文件
├── images/               # 提取的图片
└── meta.json             # 处理元数据
```

---

### 2. convert-md-to-html.py - Markdown格式化工具

**功能**: Markdown → Word/HTML/PDF（支持9种专业模板）

#### 基础用法
```bash
./convert-md-to-html.py <输入文件> [选项]
```

#### 常用参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `--template` | 指定模板 | `--template academic` |
| `-o, --output` | 输出目录 | `-o output/` |
| `--to-docx` | 自动转换为DOCX | `--to-docx` |
| `--list-templates` | 列出所有模板 | `--list-templates` |

#### 使用示例

**Markdown → Word**
```bash
# 使用学术论文模板
./convert-md-to-html.py document.md --template academic --to-docx

# 使用商务报告模板
./convert-md-to-html.py document.md --template business --to-docx

# 输出HTML（可手动转Word）
./convert-md-to-html.py document.md --template technical -o html_output/
```

**Markdown → PDF**
```bash
# 基础PDF
pandoc document.md -o document.pdf

# 高质量PDF（支持中文）
pandoc document.md -o document.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="SimSun" \
  -V geometry:margin=2cm
```

---

## 🎨 模板系统

### 9种预置模板

| 模板名称 | 适用场景 | 命令参数 |
|---------|---------|---------|
| **academic** | 学术论文、毕业论文 | `--template academic` |
| **business** | 商务报告、项目计划 | `--template business` |
| **business_modern** | 现代简约商务 | `--template business_modern` |
| **business_luxury** | 黑金轻奢商务 | `--template business_luxury` |
| **business_fresh** | 清新薄荷绿商务 | `--template business_fresh` |
| **business_neutral** | 中性灰调商务 | `--template business_neutral` |
| **technical** | 技术文档、API手册 | `--template technical` |
| **tender** | 政府采购标书 | `--template tender` |
| **official** | 党政机关公文 | `--template official` |

### 列出所有模板
```bash
./convert-md-to-html.py --list-templates
```

---

## 📚 使用场景

### 场景1：PDF转Word
```bash
# 步骤1：PDF → Markdown
./convert.py report.pdf -o output/

# 步骤2：Markdown → Word
./convert-md-to-html.py output/report.md --template business --to-docx

# 结果：report.docx
```

### 场景2：学术论文格式化
```bash
# 步骤1：PDF → Markdown（启用内容精修）
./convert.py paper.pdf --refine-content -o output/

# 步骤2：应用学术模板
./convert-md-to-html.py output/paper.md --template academic --to-docx

# 结果：paper.docx（Times New Roman + 宋体，1.5倍行距）
```

### 场景3：批量处理
```bash
# 批量PDF → Markdown
./convert.py "docs/*.pdf" --batch -o batch_md/

# 批量应用模板
for md in batch_md/*.md; do
  ./convert-md-to-html.py "$md" --template business --to-docx
done
```

### 场景4：快速预览
```bash
# 只处理前10页（快速预览效果）
./convert.py large.pdf --max-pages 10 -o preview/
```

---

## 📂 默认工作目录

项目包含三个临时工作目录（已加入.gitignore）：

| 目录 | 用途 | 说明 |
|------|------|------|
| `input/` | 输入文件 | 放置待处理的文档 |
| `output/` | 输出文件 | 存放处理结果 |
| `tmp/` | 临时文件 | 存放临时脚本和中间文件 |

### 使用示例
```bash
# 将文件放入input目录
cp ~/Documents/report.pdf input/

# 处理文件
./convert.py input/report.pdf

# 结果输出到output/
ls output/
```

### 清理工作目录
```bash
# 清理所有临时文件
rm -rf input/* output/* tmp/*
```

---

## ⚙️ 环境配置

### 必需配置
```bash
export DEEPSEEK_API_KEY="your_key"
```

### 可选配置

**启用内容精修**（默认关闭）:
```yaml
# 编辑 config/default.yaml
processing:
  pdf:
    enable_content_refinement: true
```

**自定义模板**:
```bash
# 复制并修改模板
cp config/templates/business.yaml config/templates/my_template.yaml
vim config/templates/my_template.yaml

# 使用自定义模板
./convert-md-to-html.py document.md --template my_template -o output/
```

---

## 🔧 辅助工具

### zhipu-vision - 图片查看助手

**用途**: 单独查看或分析图片内容

**使用场景**:
- 检查提取的图片质量
- 分析图片中的表格、图表
- 验证图片中的文字内容

**注意**: 正常文档转换流程已自动处理图片，此工具仅在需要单独分析图片时使用。

---

## 📖 相关文档

- **主文档**: [README.md](README.md) - 项目概览和架构
- **架构设计**: [docs/V4_ARCHITECTURE.md](docs/V4_ARCHITECTURE.md) - v4架构详情
- **模板指南**: [docs/TEMPLATE_SYSTEM_README.md](docs/TEMPLATE_SYSTEM_README.md) - 模板系统说明

---

## 📝 命令速查

### PDF/DOCX → Markdown
```bash
# 基础转换
./convert.py document.pdf -o output/

# 高质量转换
./convert.py paper.pdf --refine-content -o output/

# 限制页数
./convert.py large.pdf --max-pages 10 -o preview/

# 分页处理
./convert.py large.pdf --start-page 51 --max-pages 50 -o part2/

# 批量处理
./convert.py "docs/*.pdf" --batch -o batch_output/
```

### Markdown → Word/HTML/PDF
```bash
# Markdown → Word
./convert-md-to-html.py document.md --template academic --to-docx

# Markdown → HTML
./convert-md-to-html.py document.md --template business -o html_output/

# Markdown → PDF
pandoc document.md -o document.pdf --pdf-engine=xelatex -V CJKmainfont="SimSun"

# 列出模板
./convert-md-to-html.py --list-templates
```

---

**准备就绪！** 🚀

简单命令，完整处理。
