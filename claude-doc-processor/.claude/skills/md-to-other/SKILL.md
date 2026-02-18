---
name: md-to-other
description: 将Markdown转换为其他格式（HTML/Word/PDF）。当用户说"Markdown转Word"、"MD转HTML"、"MD转PDF"、"生成Word文档"、"生成PDF"时使用。
argument-hint: [input-file] [format] [output-dir]
allowed-tools: Bash(./convert-md-to-html.py *), Bash(pandoc:*), Bash(soffice:*)
---

# Markdown转其他格式转换器

将Markdown转换为HTML、DOCX、PDF等格式。

## Markdown → HTML (Word兼容)

```bash
./convert-md-to-html.py $ARGUMENTS
```

**场景示例**：
```bash
./convert-md-to-html.py document.md
./convert-md-to-html.py document.md -o output/
./convert-md-to-html.py document.md -o docs/
```

## Markdown → DOCX

### 方案1：HTML转DOCX（推荐，支持复杂排版）

```bash
./convert-md-to-html.py document.md -o output/
soffice --headless --convert-to docx output/document.html
```

### 方案2：Pandoc直接转DOCX（简单场景）

```bash
pandoc document.md -o document.docx
```

## Markdown → PDF

```bash
# 基础转换
pandoc document.md -o document.pdf

# 指定输出目录
pandoc document.md -o output/document.pdf

# 高质量PDF（推荐，支持中文）
pandoc document.md -o document.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="SimSun" \
  -V geometry:margin=2cm

# 包含目录
pandoc document.md -o document.pdf --toc
```
