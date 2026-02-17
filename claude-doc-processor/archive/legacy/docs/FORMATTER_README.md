# PDF 处理与格式化流程

## 两步工作流程

由于 LM Studio 一次只能加载一个模型，我们分两步完成处理：

### 步骤 1: PDF 识别（使用 GLM-4.6V）

```bash
# 在 LM Studio 中加载模型：zai-org/glm-4.6v-flash
python3 scripts/process_pdf_with_glm46v_v2.py "input_file/你的文档.pdf" -o ./output_glm
```

**参数说明：**
- `-o ./output_glm`: 输出目录
- `-n 5`: 只处理前5页（可选）
- `--api-url http://192.168.100.110:9999`: LM Studio 地址

**输出：**
- `./output_glm/文档名_时间戳/page_001.md`, `page_002.md`, ...
- `./output_glm/文档名_时间戳/文档名_full.md`

---

### 步骤 2: 格式化 Markdown（二选一）

#### 方案 A: 使用本地 LLM（推荐，免费）

```bash
# 在 LM Studio 中切换模型到：Qwen/Qwen2.5-72B-Instruct 或 gpt-oss:20b
python3 scripts/format_with_local_llm.py output_glm/*/page_001.md
```

**批量格式化所有页面：**
```bash
find output_glm/*/page_*.md -exec python3 scripts/format_with_local_llm.py {} \;
```

**格式化完整文档：**
```bash
python3 scripts/format_with_local_llm.py output_glm/*/文档名_full.md
```

#### 方案 B: 使用 Mistral AI（云端，需API密钥）

```bash
# 获取API密钥：https://console.mistral.ai/
# 或使用 ModelScope 免费API
python3 scripts/format_with_mistral_fixed.py output_glm/*/page_001.md "ms-你的API密钥"
```

**批量格式化：**
```bash
find output_glm/*/page_*.md -exec python3 scripts/format_with_mistral_fixed.py {} "ms-你的API密钥" \;
```

---

## 输出文件

格式化后会生成：`原文件名_formatted.md`

例如：`page_001.md` → `page_001_formatted.md`

## 后续处理

格式化完成后，可以使用 Typora 查看效果，或使用 pandoc 转换为其他格式：

```bash
# Markdown → PDF
pandoc page_001_formatted.md -o output.pdf --pdf-engine=xelatex

# Markdown → Word
pandoc page_001_formatted.md -o output.docx
```

## 脚本说明

| 脚本 | 用途 | 模型要求 |
|------|------|-----------|
| `process_pdf_with_glm46v_v2.py` | PDF识别 | zai-org/glm-4.6v-flash |
| `format_with_local_llm.py` | 格式化（本地）| Qwen2.5-72B / gpt-oss:20b |
| `format_with_mistral_fixed.py` | 格式化（云端）| 无需本地模型 |

## 常见问题

**Q: 本地LLM格式化时输出了思考过程？**
A: 这是 Qwen 等模型的特性，脚本会自动过滤这些内容。

**Q: LaTeX公式显示不正确？**
A: 脚本会自动修复 `\frac{a}{b}` 等常见转义问题。

**Q: 表格格式乱了？**
A: 格式化LLM会重新组织表格结构，确保符合Markdown标准。

**Q: 如何批量处理整个PDF？**
A: 使用步骤1处理完整PDF，然后使用find命令批量格式化所有页面。
