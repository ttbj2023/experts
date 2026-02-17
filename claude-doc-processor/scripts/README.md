# Scripts 目录说明

**更新时间**: 2026-02-17
**状态**: ✅ 已整理归档

---

## 📁 目录结构

```
scripts/
├── convert_pdf_complete.py          # 核心参考：PDF转Markdown（5阶段）
├── convert_docx_to_markdown_v3.py   # 核心参考：DOCX转Markdown（4阶段）
├── utils/                           # 工具模块（已迁移到src/utils/）
├── prompts/                         # 提示词模板目录
└── README.md                        # 本文件
```

---

## ⚠️ 重要说明

### ✅ 推荐使用新版本

**scripts目录仅保留核心脚本作为参考**，请优先使用重构后的新版本：

```bash
# 新版本（推荐）- 模块化架构，代码复用率85%+
./convert-pdf.py input.pdf -o output_dir
./convert-docx.py input.docx -o output_dir
```

### 📦 旧脚本已归档

所有实验性、测试性脚本已归档到 `archive/legacy/` 目录：

- **archive/legacy/scripts/** - 45个历史脚本
- **archive/legacy/docs/** - 9个历史文档

---

## 📚 核心参考脚本说明

### 1. convert_pdf_complete.py

**功能**: PDF转Markdown转换器（5阶段架构）

**阶段**:
- Stage 1: GLM-4.6V-Flash OCR识别 + 占位符
- Stage 1.5: DeepSeek排版优化（可选）
- Stage 2: OpenCV图片提取
- Stage 3: GLM-4.6V-Flash图片描述
- Stage 4: DeepSeek语义匹配
- Stage 5: 占位符替换

**代码量**: 1,072行
**状态**: ✅ 已重构到 `src/converters/pdf_converter.py` (353行)

**对比**:
| 指标 | 旧版本 | 新版本 |
|------|--------|--------|
| 代码量 | 1,072行 | 353行 |
| 重复率 | 高 | <5% |
| 模块化 | 单体 | 4个core组件 |

---

### 2. convert_docx_to_markdown_v3.py

**功能**: DOCX转Markdown转换器（4阶段v3架构）

**阶段**:
- Stage 1: LibreOffice DOCX转PDF
- Stage 2: GLM-4.6V-Flash识别PDF
- Stage 3: GLM-4.6V-Flash描述图片
- Stage 4: 智能占位符替换（含代码块清理、重复检测）

**代码量**: 1,220行
**状态**: ✅ 已重构到 `src/converters/docx_converter.py` (368行)

**对比**:
| 指标 | 旧版本 | 新版本 |
|------|--------|--------|
| 代码量 | 1,220行 | 368行 |
| 重复率 | 高 | <5% |
| 模块化 | 单体 | 2个core组件 |

---

## 🗂️ 归档内容详情

### archive/legacy/scripts/ (45个文件)

**版本演进脚本（7个）**:
- `process_pdf_with_glm46v.py` - GLM-4.6V初版
- `process_pdf_with_glm46v_v2.py` - v2版
- `process_pdf_with_glm46v_v2_simple.py` - v2简化版
- `process_pdf_with_glm46v_universal.py` - 通用版本
- `process_pdf_simple.py` - 简化版
- `process_pdf_to_html_with_glm46v.py` - HTML输出版
- `process_pdf_with_qwen3vl.py` - Qwen3VL模型版

**测试脚本（9个）**:
- `test_api_response.py`
- `test_compression.py`
- `test_docx_conversion.sh`
- `test_final_postprocess.py`
- `test_full_response.py`
- `test_llm_connection.py`
- `test_math_textbook_prompt.sh`
- `test_page_12_repeat.sh`
- `test_qwen3vl.sh`

**格式化脚本（6个）**:
- `format_markdown_with_deepseek.py`
- `format_with_local_llm.py`
- `format_with_mistral.py` / `format_with_mistral_fixed.py`
- `format_with_ollama.py`

**后处理脚本（2个）**:
- `post_processor.py`
- `post_processor_logic.py`

**图片处理脚本（4个）**:
- `analyze_all_images.py`
- `analyze_images_latex.py`
- `extract_images_from_pdf.py`
- `debug_image28.py`

**修复工具（3个）**:
- `fix_markdown_tables.py` / `fix_markdown_tables_v2.py`
- `fix_latex_rendering.py`
- `clean_thinking.py`

**其他工具（4个）**:
- `deepseek_matcher.py`
- `ollama_simple.py`
- `latex_to_word_formula.py`
- `convert_md_to_docx.py`
- `convert_md_to_html_enhanced.py`

**批处理脚本（12个）**:
- `batch_convert_docx_to_md.sh`
- `batch_process_pdfs.sh`
- `compare_models.sh`
- `config_qwen3vl.sh`
- `convert_md_to_docx_quick.sh`
- `convert_md_to_pdf.sh`
- `monitor_progress.sh`
- `validate_output.sh`
- 以及4个test_*.sh脚本

---

### archive/legacy/docs/ (9个文档)

**转换指南**:
- `DOCX_CONVERSION_GUIDE.md` - DOCX转换指南
- `DOCX_CONVERSION_SUMMARY.md` - DOCX转换总结
- `DOCX_TO_MARKDOWN_README.md` - DOCX转Markdown说明
- `README_convert_docx_to_markdown_v3.md` - v3版README

**格式化文档**:
- `FORMATTER_README.md` - 格式化工具说明

**版本对比**:
- `GLM46V_VERSION_COMPARISON.md` - GLM-4.6V版本对比
- `UNIVERSAL_VERSION_QUICKSTART.md` - 通用版本快速开始

**Ollama相关**:
- `OLLAMA_QUICKSTART.md` - Ollama快速开始
- `OLLAMA_SETUP.md` - Ollama安装配置

---

## 📊 归档统计

| 类别 | 文件数 | 说明 |
|------|--------|------|
| **保留核心脚本** | 2 | convert_pdf_complete.py, convert_docx_to_markdown_v3.py |
| **归档脚本** | 45 | 版本演进、测试、工具、批处理 |
| **归档文档** | 9 | 使用指南、版本说明、配置文档 |
| **保留目录** | 2 | utils/, prompts/ |
| **总计** | 58 | |

---

## 🎯 使用建议

### ✅ 日常使用（推荐）

**优先使用新版本**：
```bash
# 新版本 - 模块化、可维护、配置灵活
./convert-pdf.py input.pdf -o output
./convert-docx.py input.docx -o output
```

### 📖 参考学习

**阅读核心脚本**：
- 理解5阶段PDF处理流程 → `convert_pdf_complete.py`
- 理解4阶段DOCX处理流程 → `convert_docx_to_markdown_v3.py`
- 查看版本演进历史 → `archive/legacy/scripts/process_pdf_*.py`

### 🔍 历史研究

**查阅归档内容**：
- 版本对比 → `archive/legacy/docs/GLM46V_VERSION_COMPARISON.md`
- 使用指南 → `archive/legacy/docs/*.md`
- 实验性功能 → `archive/legacy/scripts/`

---

## 🚀 迁移建议

### 从旧版本迁移到新版本

**1. PDF转换**：
```bash
# 旧版本（scripts/）
python scripts/convert_pdf_complete.py input.pdf

# 新版本（推荐）
./convert-pdf.py input.pdf -o output_dir
```

**2. DOCX转换**：
```bash
# 旧版本（scripts/）
python scripts/convert_docx_to_markdown_v3.py input.docx

# 新版本（推荐）
./convert-docx.py input.docx -o output_dir
```

**3. 配置迁移**：
- 旧版本：硬编码在脚本中
- 新版本：使用 `config/default.yaml` + 环境变量

**4. 自定义扩展**：
- 旧版本：修改脚本代码
- 新版本：继承 `BaseConverter` 或修改配置文件

---

## 📝 维护说明

### 保留内容

**核心脚本（不删除）**：
- ✅ `convert_pdf_complete.py` - PDF转换参考实现
- ✅ `convert_docx_to_markdown_v3.py` - DOCX转换参考实现
- ✅ `utils/` - 工具模块（虽然已迁移到src/）
- ✅ `prompts/` - 提示词模板

### 归档内容

**不删除，仅归档**：
- ✅ 所有实验性脚本
- ✅ 所有测试脚本
- ✅ 所有辅助工具脚本
- ✅ 所有批处理脚本
- ✅ 所有历史文档

### 清理内容

**已删除**：
- ❌ `.backup` 备份文件
- ❌ `Zone.Identifier` Windows标识文件
- ❌ `__pycache__` Python缓存

---

## 🔗 相关链接

- **重构计划**: `docs/REFACTOR_PLAN.md`
- **新版本源码**: `src/`
- **配置文件**: `config/default.yaml`
- **主文档**: `README.md`

---

**维护者**: Claude Code
**最后更新**: 2026-02-17
**归档状态**: ✅ 完成
