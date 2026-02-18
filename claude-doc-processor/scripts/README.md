# Scripts 目录说明

**更新时间**: 2026-02-18
**状态**: ✅ 已整理

---

## 📁 目录结构

```
scripts/
├── ai_workflow_example.sh      # AI工作流示例脚本
├── README.md                    # 本文件
└── prompts/                     # 提示词模板
    ├── fix_format_prompt.txt
    ├── math_textbook_v3.txt
    └── README.md
```

---

## ✅ 推荐使用

**v4.0统一架构（推荐）**：
```bash
# 统一转换器 - 支持PDF和DOCX
./convert.py input.pdf -o output_dir
./convert.py input.docx -o output_dir

# Markdown转其他格式
./convert-md-to-html.py document.md --template academic -o output/
```

---

## 📚 当前内容说明

### 1. ai_workflow_example.sh
**用途**: AI工作流示例脚本

**功能**: 展示如何组合使用多个处理阶段，包括：
- PDF类型检测
- 图片提取
- OCR识别
- 内容优化
- 格式转换

**使用**: 参考脚本中的示例命令和注释

---

### 2. prompts/ (提示词模板)

用于AI模型的提示词配置，已集成到 `convert.py` 的处理流程中。

#### math_textbook_v3.txt
**用途**: 数学教材处理提示词

**特性**:
- 页眉页脚自动过滤
- 注释性双栏智能处理
- 题目编号完整保护
- 数学公式精确LaTeX化
- 禁止代码块误识别

**适用**: 数学教辅材料、含双栏注释的教材

#### fix_format_prompt.txt
**用途**: 格式修复提示词

**功能**:
- Markdown格式修复
- 表格分隔行补全
- 代码块格式修正
- 标题层级规范化

---

## 🗂️ 历史归档

旧版本的脚本和文档已归档到以下位置：

### archive/legacy/scripts/ (45个文件)
**版本演进脚本（7个）**:
- `process_pdf_with_glm46v.py` - GLM-4.6V初版
- `process_pdf_with_glm46v_v2.py` - v2版
- `process_pdf_with_qwen3vl.py` - Qwen3VL模型版
- 等...

**测试脚本（9个）**:
- `test_math_textbook_prompt.sh`
- `test_qwen3vl.sh`
- 等...

**格式化、后处理、图片处理、批处理脚本**:
- 共45个历史脚本

### archive/legacy/scripts_utils/
**工具模块（已迁移到src/utils/）**:
- `image_analyzer.py` - 图片分析工具
- `embed_images_intelligently.py` - 智能嵌入图片
- `omml_converter.py` - OMML转换器

**说明**: v4.0重构时迁移到 `src/utils/`，原版本已归档

### archive/legacy/docs/ (9个文档)
- 转换指南、版本说明、配置文档

### archive/legacy_docs/prompts/
**提示词相关归档**:
- `CHANGELOG_v3.md` - v3提示词更新日志

### archive/legacy_docs/experiments/
**实验性功能测试**:
- `QWEN3VL_TEST.md` - Qwen3-VL模型测试指南

---

## 🔍 查看归档内容

**浏览归档脚本**：
```bash
# 查看所有归档脚本
ls -la archive/legacy/scripts/

# 查看版本演进历史
ls archive/legacy/scripts/process_pdf_*.py
```

**查看归档文档**：
```bash
# 查看历史文档
ls archive/legacy/docs/

# 阅读特定文档
cat archive/legacy/docs/GLM46V_VERSION_COMPARISON.md
```

---

## 📖 参考资料

### 核心文档
- **主文档**: `README.md` - 项目概览
- **使用指南**: `CLAUDE.md` - Claude工作区使用指南
- **架构设计**: `docs/V4_ARCHITECTURE.md` - v4.0架构设计

### 配置文件
- **主配置**: `config/default.yaml`
- **模板配置**: `config/templates/`

### 源代码
- **转换器**: `src/converters/unified_converter.py`
- **核心引擎**: `src/core/`
- **工具函数**: `src/utils/`（包含image_analyzer, embed_images_intelligently等）

---

## 🚀 从旧版本迁移

### 旧脚本 → 新版本

```bash
# ❌ 旧版本（已归档）
python scripts/process_pdf_with_glm46v_v2.py input.pdf
python scripts/convert_pdf_complete.py input.pdf

# ✅ 新版本（推荐）- v4.0统一架构
./convert.py input.pdf -o output_dir
./convert.py input.docx -o output_dir
```

### 配置方式变化

| 项目 | 旧版本 | 新版本 |
|------|--------|--------|
| 配置文件 | 硬编码在脚本中 | `config/default.yaml` |
| 环境变量 | 脚本内定义 | 系统环境变量 + YAML |
| 自定义 | 修改脚本代码 | 继承`BaseConverter`或修改配置 |

---

## 💡 使用建议

### ✅ 日常使用
**优先使用统一转换器**：
```bash
./convert.py input.pdf -o output --refine-content
```

### 📖 参考学习
**阅读归档脚本了解历史**：
- 查看5阶段PDF处理流程 → `archive/legacy/scripts/convert_pdf_complete.py`
- 查看版本演进 → `archive/legacy/scripts/process_pdf_*.py`
- 查看测试方法 → `archive/legacy/scripts/test_*.sh`

### 🔍 历史研究
**查阅归档内容**：
- 版本对比 → `archive/legacy/docs/GLM46V_VERSION_COMPARISON.md`
- 使用指南 → `archive/legacy/docs/*.md`
- 实验性功能 → `archive/legacy_docs/experiments/`

---

**维护者**: Claude Code
**最后更新**: 2026-02-18
**归档状态**: ✅ 完成
