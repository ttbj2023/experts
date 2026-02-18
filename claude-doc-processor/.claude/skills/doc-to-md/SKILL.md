---
name: doc-to-md
description: 将PDF/DOCX文档转换为高质量Markdown。支持OCR识别、图片提取、格式优化。当用户说"转换文档"、"PDF转Markdown"、"DOCX转MD"、"处理这份文档"时使用。
argument-hint: [input-file] [output-dir]
allowed-tools: Bash(./convert.py *)
---

# 文档转Markdown转换器

使用Claude Doc Processor v4.0将PDF或DOCX转换为高质量Markdown。

## 智能参数选择

根据用户需求自动添加参数：

### 质量要求
- **用户说"高质量"、"精确"、"优化"** → 添加 `--refine-content`
- **用户说"快速"、"预览"** → 添加 `--max-pages 10`

### 批量处理
- **用户说"批量"、"所有"、"多个"** → 添加 `--batch`
- **通配符模式** → 添加 `--batch`

### 限制条件
- **用户指定页数** → 添加 `--max-pages N`
- **用户说"从第X页开始"、"从X页起"** → 添加 `--start-page X`
- **用户说"详细"** → 添加 `--verbose`

## 命令用法

### 基础转换
```bash
./convert.py $ARGUMENTS
```

### 场景示例

**单个文档转换**
```bash
./convert.py document.pdf
./convert.py document.docx -o output/
```

**高质量转换（启用Stage 3.5内容精修）**
```bash
./convert.py document.pdf --refine-content
./convert.py paper.pdf --refine-content -o academic/
```

**批量转换**
```bash
./convert.py "docs/*.pdf" --batch -o batch_output/
./convert.py "documents/*.*" --batch -o converted/
```

**快速预览（限制页数）**
```bash
./convert.py document.pdf --max-pages 5
./convert.py large_doc.pdf --max-pages 10 -o preview/
```

**分页处理（从指定页开始）**
```bash
# 从第51页开始处理50页
./convert.py large.pdf --start-page 51 --max-pages 50

# 大文档分批处理
./convert.py large.pdf --start-page 1 --max-pages 100 -o part1/
./convert.py large.pdf --start-page 101 --max-pages 100 -o part2/

# 断点续传（从断点继续）
./convert.py large.pdf --start-page 501 -o continue/
```

**指定输出目录**
```bash
./convert.py document.md -o custom_output/
```
