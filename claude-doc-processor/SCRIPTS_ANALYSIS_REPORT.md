# Scripts 目录分析报告

生成时间：2026-02-17
目录：scripts/

## 📊 总体统计

### 文件数量
- **Python脚本**: 38个
- **Shell脚本**: 17个
- **Markdown文档**: 10个
- **文本文件**: 2个
- **其他**: 3个（backup文件、Zone.Identifier）
- **总计**: 70个文件 + 2个子目录

### 子目录
- `prompts/`: 4个文件（提示词配置）
- `utils/`: 6个文件（工具函数库）
- `__pycache__/`: Python缓存目录

## 🗂️ 详细分类

### 1. 核心转换脚本（4个）✅ 保留

| 文件名 | 大小 | 功能 | 状态 |
|--------|------|------|------|
| `convert_docx_to_markdown_v3.py` | 47K | DOCX→MD v3版本（三阶段架构） | ✅ **生产使用** |
| `convert_pdf_complete.py` | 35K | PDF完整转换工具 | ✅ **生产使用** |
| `convert_md_to_docx.py` | 8.1K | MD→DOCX基础版本 | ✅ **保留** |
| `convert_md_to_html_enhanced.py` | 18K | MD→HTML增强版 | ✅ **保留** |

### 2. 批量处理脚本（2个）✅ 保留

| 文件名 | 大小 | 功能 | 状态 |
|--------|------|------|------|
| `batch_convert_docx_to_md.sh` | 5.1K | 批量DOCX转MD | ✅ **保留** |
| `batch_process_pdfs.sh` | 1.3K | 批量PDF处理 | ✅ **保留** |

### 3. PDF处理脚本（9个）⚠️ 整理

| 文件名 | 大小 | 功能 | 建议 |
|--------|------|------|------|
| `extract_images_from_pdf.py` | 14K | 从PDF提取图片 | ✅ **保留**（独特功能） |
| `process_pdf_simple.py` | 14K | 简化PDF处理 | 📦 **归档**（被complete替代） |
| `process_pdf_to_html_with_glm46v.py` | 16K | GLM-4.6V PDF→HTML | 📦 **归档**（特定用途） |
| `process_pdf_with_glm46v.py` | 8.2K | GLM-4.6V基础处理 | 📦 **归档**（旧版本） |
| `process_pdf_with_glm46v_universal.py` | 17K | 通用版本 | ✅ **保留**（universal） |
| `process_pdf_with_glm46v_v2.py` | 20K | v2版本 | 📦 **归档**（已被universal替代） |
| `process_pdf_with_glm46v_v2.py.backup` | 13K | v2备份 | 🗑️ **删除** |
| `process_pdf_with_glm46v_v2_simple.py` | 14K | v2简化版 | 📦 **归档** |
| `process_pdf_with_qwen3vl.py` | 17K | Qwen3VL模型处理 | 📦 **归档**（备选方案） |

**整理后保留**：
- `extract_images_from_pdf.py`（独特功能）
- `process_pdf_with_glm46v_universal.py`（通用版本）

### 4. 格式化/后处理脚本（12个）⚠️ 整理

| 文件名 | 大小 | 功能 | 建议 |
|--------|------|------|------|
| `format_markdown_with_deepseek.py` | 8.1K | DeepSeek格式化 | ✅ **保留**（生产使用） |
| `format_with_local_llm.py` | 8.1K | 本地LLM格式化 | ✅ **保留**（本地模型） |
| `format_with_mistral.py` | 6.7K | Mistral格式化 | 📦 **归档**（旧版本） |
| `format_with_mistral_fixed.py` | 7.6K | Mistral修复版 | 📦 **归档** |
| `format_with_ollama.py` | 6.7K | Ollama格式化 | ✅ **保留**（Ollama生态） |
| `clean_thinking.py` | 3.0K | 清理思考过程 | ✅ **保留**（实用工具） |
| `fix_latex_rendering.py` | 3.4K | 修复LaTeX渲染 | ✅ **保留**（专用功能） |
| `fix_markdown_tables.py` | 4.2K | 修复Markdown表格 | ✅ **保留** |
| `fix_markdown_tables_v2.py` | 2.5K | 表格修复v2 | 📦 **归档**（旧版本） |
| `latex_to_word_formula.py` | 3.4K | LaTeX转Word公式 | ✅ **保留**（独特功能） |
| `post_processor.py` | 1.2K | 后处理基础版 | 📦 **归档**（功能简单） |
| `post_processor_logic.py` | 707B | 后处理逻辑 | 📦 **归档**（功能简单） |

**整理后保留**：
- `format_markdown_with_deepseek.py`（生产使用）
- `format_with_local_llm.py`（本地模型）
- `format_with_ollama.py`（Ollama生态）
- `clean_thinking.py`（实用工具）
- `fix_latex_rendering.py`（专用功能）
- `fix_markdown_tables.py`（表格修复）
- `latex_to_word_formula.py`（独特功能）

### 5. 测试脚本（12个）⚠️ 全部归档

| 文件名 | 大小 | 类型 | 建议 |
|--------|------|------|------|
| `test_api_response.py` | 2.5K | API测试 | 📦 **归档** |
| `test_compression.py` | 2.0K | 压缩测试 | 📦 **归档** |
| `test_docx_conversion.sh` | 3.7K | 转换测试 | 📦 **归档** |
| `test_final_postprocess.py` | 438B | 后处理测试 | 📦 **归档** |
| `test_full_response.py` | 1.4K | 响应测试 | 📦 **归档** |
| `test_llm_connection.py` | 1.6K | 连接测试 | 📦 **归档** |
| `test_math_textbook_prompt.sh` | 3.1K | 提示词测试 | 📦 **归档** |
| `test_page_12_repeat.sh` | 4.1K | 页面重复测试 | 📦 **归档** |
| `test_qwen3vl.sh` | 3.0K | Qwen3VL测试 | 📦 **归档** |
| `debug_image28.py` | 6.4K | 调试脚本 | 📦 **归档** |
| `analyze_all_images.py` | 7.8K | 图片分析 | 📦 **归档** |
| `analyze_images_latex.py` | 12K | LaTeX图片分析 | 📦 **归档** |

### 6. 配置/监控脚本（5个）⚠️ 整理

| 文件名 | 大小 | 功能 | 建议 |
|--------|------|------|------|
| `compare_models.sh` | 3.5K | 模型对比 | 📦 **归档**（临时工具） |
| `config_qwen3vl.sh` | 1.1K | Qwen3VL配置 | 📦 **归档**（备选方案） |
| `monitor_progress.sh` | 1.4K | 进度监控 | ✅ **保留**（实用工具） |
| `validate_output.sh` | 2.5K | 输出验证 | ✅ **保留**（质量保证） |
| `watch_model_switch.py` | 2.3K | 模型切换监控 | 📦 **归档**（调试工具） |

**整理后保留**：
- `monitor_progress.sh`（实用工具）
- `validate_output.sh`（质量保证）

### 7. 文档文件（10个）✅ 保留/整理

| 文件名 | 大小 | 类型 | 建议 |
|--------|------|------|------|
| `README_convert_docx_to_markdown_v3.md` | 8.3K | v3版本说明 | ✅ **保留** |
| `DOCX_CONVERSION_GUIDE.md` | 5.0K | DOCX转换指南 | ✅ **保留** |
| `DOCX_CONVERSION_SUMMARY.md` | 8.7K | DOCX转换总结 | ✅ **保留** |
| `DOCX_TO_MARKDOWN_README.md` | 10K | DOCX→MD说明 | 📦 **归档**（重复内容） |
| `FORMATTER_README.md` | 2.7K | 格式化工具说明 | ✅ **保留** |
| `OLLAMA_QUICKSTART.md` | 2.0K | Ollama快速开始 | ✅ **保留** |
| `OLLAMA_SETUP.md` | 1.6K | Ollama安装指南 | ✅ **保留** |
| `GLM46V_VERSION_COMPARISON.md` | 8.1K | GLM-4.6V版本对比 | 📦 **归档**（历史文档） |
| `UNIVERSAL_VERSION_QUICKSTART.md` | 6.0K | Universal版本指南 | ✅ **保留** |
| `fix_format_prompt.txt` | 2.7K | 格式修复提示词 | ✅ **保留** |

**整理后保留**：
- `README_convert_docx_to_markdown_v3.md`
- `DOCX_CONVERSION_GUIDE.md`
- `DOCX_CONVERSION_SUMMARY.md`
- `FORMATTER_README.md`
- `OLLAMA_QUICKSTART.md`
- `OLLAMA_SETUP.md`
- `UNIVERSAL_VERSION_QUICKSTART.md`
- `fix_format_prompt.txt`

### 8. 工具脚本（1个）✅ 保留

| 文件名 | 大小 | 功能 | 建议 |
|--------|------|------|------|
| `deepseek_matcher.py` | 8.7K | DeepSeek语义匹配 | ✅ **保留**（核心功能） |
| `convert_md_to_docx_quick.sh` | 3.9K | MD→DOCX快速转换 | ✅ **保留** |
| `convert_md_to_pdf.sh` | 2.4K | MD→PDF转换 | ✅ **保留** |

### 9. utils/ 子目录（6个文件）✅ 全部保留

| 文件名 | 大小 | 功能 | 建议 |
|--------|------|------|------|
| `cleanup_md.py` | 2.0K | MD清理工具 | ✅ **保留** |
| `embed_images_intelligently.py` | 8.8K | 智能图片嵌入 | ✅ **保留** |
| `image_analyzer.py` | 9.5K | 图片分析器 | ✅ **保留** |
| `image_optimizer.py` | 7.5K | 图片优化器 | ✅ **保留** |
| `omml_converter.py` | 12K | OMML转换器 | ✅ **保留** |
| `pdf_image_extractor.py` | 6.5K | PDF图片提取 | ✅ **保留** |

### 10. prompts/ 子目录（4个文件）✅ 全部保留

| 文件名 | 大小 | 功能 | 建议 |
|--------|------|------|------|
| `CHANGELOG.md` | 5.1K | 变更日志 | ✅ **保留** |
| `math_textbook_v3.txt` | 2.7K | 数学教材提示词v3 | ✅ **保留** |
| `QWEN3VL_TEST.md` | 5.7K | Qwen3VL测试提示词 | ✅ **保留** |
| `README.md` | 6.6K | 提示词说明 | ✅ **保留** |

### 11. 临时/备份文件（3个）🗑️ 删除

| 文件名 | 大小 | 类型 | 建议 |
|--------|------|------|------|
| `convert_pdf_complete.py.backup` | 31K | 备份文件 | 🗑️ **删除** |
| `validate_output.sh:Zone.Identifier` | 0B | 系统文件 | 🗑️ **删除** |

## 📈 整理方案

### 方案A：彻底整理（推荐）

#### 整理前后对比

| 分类 | 整理前 | 整理后 | 减少 |
|------|--------|--------|------|
| 核心转换 | 4 | 4 | 0 |
| PDF处理 | 9 | 2 | **77%** |
| 格式化工具 | 12 | 7 | **42%** |
| 测试脚本 | 12 | 0 | **100%** |
| 配置监控 | 6 | 3 | **50%** |
| 文档文件 | 10 | 8 | **20%** |
| 工具脚本 | 3 | 3 | 0 |
| utils/ | 6 | 6 | 0 |
| prompts/ | 4 | 4 | 0 |
| 临时文件 | 3 | 0 | **100%** |
| **总计** | **69** | **37** | **46%** |

#### 执行步骤

**1. 创建归档目录**
```bash
mkdir -p archive/legacy/scripts/pdf_processing
mkdir -p archive/legacy/scripts/formatting
mkdir -p archive/legacy/scripts/tests
mkdir -p archive/legacy/scripts/config
mkdir -p archive/legacy/scripts/docs
```

**2. 归档PDF处理脚本（7个）**
```bash
# 归档到 archive/legacy/scripts/pdf_processing/
mv process_pdf_simple.py process_pdf_to_html_with_glm46v.py \
   process_pdf_with_glm46v.py process_pdf_with_glm46v_v2.py \
   process_pdf_with_glm46v_v2_simple.py process_pdf_with_qwen3vl.py \
   archive/legacy/scripts/pdf_processing/
```

**3. 归档格式化工具（5个）**
```bash
# 归档到 archive/legacy/scripts/formatting/
mv format_with_mistral.py format_with_mistral_fixed.py \
   fix_markdown_tables_v2.py post_processor.py post_processor_logic.py \
   archive/legacy/scripts/formatting/
```

**4. 归档测试脚本（12个）**
```bash
# 归档到 archive/legacy/scripts/tests/
mv test_*.py test_*.sh debug_*.py analyze_*.py \
   archive/legacy/scripts/tests/
```

**5. 归档配置脚本（3个）**
```bash
# 归档到 archive/legacy/scripts/config/
mv compare_models.sh config_qwen3vl.sh watch_model_switch.py \
   archive/legacy/scripts/config/
```

**6. 归档文档文件（2个）**
```bash
# 归档到 archive/legacy/scripts/docs/
mv DOCX_TO_MARKDOWN_README.md GLM46V_VERSION_COMPARISON.md \
   archive/legacy/scripts/docs/
```

**7. 删除临时文件（2个）**
```bash
rm convert_pdf_complete.py.backup
rm validate_output.sh:Zone.Identifier
```

**8. 清理缓存目录**
```bash
rm -rf scripts/__pycache__
```

**9. 创建scripts/README.md**
记录保留文件的功能说明和目录结构

### 方案B：最小整理

只删除临时文件：
```bash
rm convert_pdf_complete.py.backup
rm *:Zone.Identifier
rm -rf __pycache__
```

保留所有脚本，仅减少3个文件。

## 📁 整理后的目录结构

### scripts/ (37个文件)

```
scripts/
├── 核心转换（4个）
│   ├── convert_docx_to_markdown_v3.py
│   ├── convert_pdf_complete.py
│   ├── convert_md_to_docx.py
│   └── convert_md_to_html_enhanced.py
│
├── PDF处理（2个）
│   ├── extract_images_from_pdf.py
│   └── process_pdf_with_glm46v_universal.py
│
├── 批量处理（2个）
│   ├── batch_convert_docx_to_md.sh
│   └── batch_process_pdfs.sh
│
├── 格式化工具（7个）
│   ├── format_markdown_with_deepseek.py
│   ├── format_with_local_llm.py
│   ├── format_with_ollama.py
│   ├── clean_thinking.py
│   ├── fix_latex_rendering.py
│   ├── fix_markdown_tables.py
│   └── latex_to_word_formula.py
│
├── 工具脚本（3个）
│   ├── deepseek_matcher.py
│   ├── convert_md_to_docx_quick.sh
│   └── convert_md_to_pdf.sh
│
├── 配置监控（2个）
│   ├── monitor_progress.sh
│   └── validate_output.sh
│
├── 文档文件（8个）
│   ├── README_convert_docx_to_markdown_v3.md
│   ├── DOCX_CONVERSION_GUIDE.md
│   ├── DOCX_CONVERSION_SUMMARY.md
│   ├── FORMATTER_README.md
│   ├── OLLAMA_QUICKSTART.md
│   ├── OLLAMA_SETUP.md
│   ├── UNIVERSAL_VERSION_QUICKSTART.md
│   └── fix_format_prompt.txt
│
├── prompts/（4个文件）
│   ├── CHANGELOG.md
│   ├── math_textbook_v3.txt
│   ├── QWEN3VL_TEST.md
│   └── README.md
│
└── utils/（6个文件）
    ├── cleanup_md.py
    ├── embed_images_intelligently.py
    ├── image_analyzer.py
    ├── image_optimizer.py
    ├── omml_converter.py
    └── pdf_image_extractor.py
```

### archive/legacy/scripts/ (32个文件)

```
archive/legacy/scripts/
├── pdf_processing/（7个）
├── formatting/（5个）
├── tests/（12个）
├── config/（3个）
└── docs/（2个）
```

## 💡 关键发现

### 1. 版本迭代明显
- PDF处理脚本有多个版本（v1, v2, universal）
- 格式化工具有多个模型版本（Mistral, Ollama, Local LLM）
- 建议保留最新和最通用的版本

### 2. 测试文件过多
- 12个测试脚本占用空间
- 测试应在tests/目录，不应在生产scripts/中
- 建议全部归档

### 3. 文档重复
- 多个DOCX转换文档内容重复
- 建议归档历史文档，保留最新版本

### 4. 工具函数库完善
- utils/目录功能完善，应保留
- prompts/目录管理规范，应保留

## ⚠️ 注意事项

1. **备份优先**: 整理前建议创建Git提交
2. **依赖检查**: 归档脚本前检查是否有其他脚本依赖
3. **引用更新**: 更新相关文档中的脚本引用
4. **测试验证**: 整理后测试保留脚本的完整性

## 🎯 推荐方案

**推荐方案A（彻底整理）**：
- 减少46%的文件数量（69→37）
- 保留所有核心功能
- 归档所有测试和旧版本
- 提升目录可维护性

---

**报告生成者**: Claude Code
**日期**: 2026-02-17
**推荐方案**: 方案A（彻底整理）
