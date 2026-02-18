# 项目目录整理建议报告

生成时间：2026-02-17
项目：claude-doc-processor

## 📋 发现的问题

### 1. 测试目录散乱（6个）

| 目录名 | 内容 | 问题 | 建议 |
|--------|------|------|------|
| `test_docx_conversion/` | 6项 | 临时测试目录 | 📦 **归档** |
| `test_new_prompt/` | 8项 | 临时测试目录 | 📦 **归档** |
| `test_universal/` | 1项 | 临时测试目录 | 📦 **归档** |
| `test_universal_full/` | 1项 | 临时测试目录 | 📦 **归档** |
| `test_universal_output/` | 1项 | 测试输出 | 📦 **归档** |
| `test_v2/` | 1项 | 版本测试目录 | 📦 **归档** |
| `tests/` | - | 正式测试目录 | ✅ **保留** |

### 2. 文档文件杂乱（7个）

**根目录文档文件**：

| 文件名 | 大小 | 类型 | 建议 |
|--------|------|------|------|
| `ARCHIVE_CLEANUP_REPORT.md` | 6.4K | 归档报告 | 📂 `docs/reports/` |
| `DEVELOPMENT_PROGRESS.md` | 6.9K | 进度文档 | 📂 `docs/reports/` |
| `GLM46V_PROCESSING_REPORT.md` | 4.7K | 技术报告 | 📂 `docs/reports/` |
| `PDF2HTML_QUICK_GUIDE.md` | 5.0K | 快速指南 | 📂 `docs/guides/` |
| `PDF2HTML_RESEARCH_REPORT.md` | 19K | 研究报告 | 📂 `docs/reports/` |
| `README_PDF2HTML.md` | 8.1K | 功能说明 | 📂 `docs/` |
| `CLAUDE.md` | 4.9K | 项目指令 | ✅ **根目录保留** |
| `README.md` | - | 项目说明 | ✅ **根目录保留** |

### 3. 临时和调试文件（9个）

| 文件名 | 大小 | 类型 | 建议 |
|--------|------|------|------|
| `debug_cropped_table.png` | 236B | 调试图片 | 🗑️ **删除** |
| `debug_page_with_boxes.png` | 711KB | 调试图片 | 📂 `output/debug/` |
| `debug_raw_response.txt` | 84B | 调试日志 | 🗑️ **删除** |
| `deepseek_match_result.json` | 6.4KB | 测试结果 | 📂 `output/debug/` |
| `image_latex_analysis.json` | 19KB | 分析结果 | 📂 `output/debug/` |
| `image_latex_analysis_v2.log` | 62KB | 日志文件 | 📂 `output/debug/` |
| `image_latex_analysis_v3.log` | 64KB | 日志文件 | 📂 `output/debug/` |
| `image_latex_analysis_v4.log` | 63KB | 日志文件 | 📂 `output/debug/` |
| `test_universal.log` | 1KB | 测试日志 | 📂 `output/debug/` |

### 4. Zone.Identifier 文件（2个）

Windows系统安全标识符文件，应该删除：

| 文件名 | 建议 |
|--------|------|
| `CLAUDE.md:Zone.Identifier` | 🗑️ **删除** |
| `README.md:Zone.Identifier` | 🗑️ **删除** |

### 5. 散落的脚本和配置

| 文件名 | 问题 | 建议 |
|--------|------|------|
| `test_simplified_postprocess.py` | 测试脚本在根目录 | 📂 `tests/` |
| `requirements_new.txt` | 依赖文件重复 | 🔄 合并到 `requirements.txt` |
| `cli.py` | CLI工具 | ⚠️ **评估用途** |

### 6. 带时间戳的临时目录

| 目录名 | 问题 | 建议 |
|--------|------|------|
| `docx_comparison_20260215_151134/` | 临时对比目录 | 📦 **归档** |

## 🎯 整理方案

### 方案A：彻底整理（推荐）

#### 1. 创建目录结构

```bash
mkdir -p tests/legacy
mkdir -p docs/reports
mkdir -p docs/guides
mkdir -p output/debug
```

#### 2. 归档测试目录

```bash
# 移动所有test_*目录到tests/legacy/
mv test_docx_conversion tests/legacy/
mv test_new_prompt tests/legacy/
mv test_universal tests/legacy/
mv test_universal_full tests/legacy/
mv test_universal_output tests/legacy/
mv test_v2 tests/legacy/

# 移动带时间戳的目录
mv docx_comparison_20260215_151134 tests/legacy/
```

#### 3. 整理文档文件

```bash
# 移动报告文档
mv ARCHIVE_CLEANUP_REPORT.md docs/reports/
mv DEVELOPMENT_PROGRESS.md docs/reports/
mv GLM46V_PROCESSING_REPORT.md docs/reports/
mv PDF2HTML_RESEARCH_REPORT.md docs/reports/

# 移动指南文档
mv PDF2HTML_QUICK_GUIDE.md docs/guides/

# 移动功能说明
mv README_PDF2HTML.md docs/
```

#### 4. 整理调试文件

```bash
# 移动有价值的调试文件到output/debug/
mv debug_page_with_boxes.png output/debug/
mv deepseek_match_result.json output/debug/
mv image_latex_analysis.json output/debug/
mv image_latex_analysis_v*.log output/debug/
mv test_universal.log output/debug/

# 删除无价值的调试文件
rm debug_cropped_table.png
rm debug_raw_response.txt
```

#### 5. 清理系统文件

```bash
# 删除Zone.Identifier文件
rm *:Zone.Identifier
```

#### 6. 整理脚本

```bash
# 移动测试脚本
mv test_simplified_postprocess.py tests/
```

### 方案B：最小整理（快速）

只删除明显无用的文件：

```bash
# 删除Zone.Identifier文件
rm *:Zone.Identifier

# 删除无价值的调试文件
rm debug_cropped_table.png
rm debug_raw_response.txt

# 移动所有调试文件到一个目录
mkdir -p debug_temp
mv debug_* debug_temp/
mv image_latex_analysis* debug_temp/
mv deepseek_match_result.json debug_temp/
mv test_universal.log debug_temp/
```

## 📊 整理效果对比

### 方案A（彻底整理）

| 项目 | 整理前 | 整理后 | 改善 |
|------|--------|--------|------|
| 根目录文件 | 20+ | 4 | **减少80%** |
| 测试目录 | 7个散乱 | 1个集中 | **减少86%** |
| 文档文件 | 根目录散乱 | docs/分类 | **100%规范** |
| 临时文件 | 根目录散乱 | output/debug | **100%规范** |

### 方案B（最小整理）

- 只删除无用文件
- 快速减少杂乱
- 适合临时清理

## ⚠️ 注意事项

1. **备份优先**: 整理前建议创建Git提交或备份
2. **依赖检查**: 移动requirements文件前检查依赖
3. **引用检查**: 移动文档后检查是否有内部链接
4. **脚本检查**: 确认cli.py的用途后再决定

## 🔄 回滚方案

如果整理后有问题，可以通过Git回滚：

```bash
# 查看整理前的状态
git status

# 回滚特定文件
git checkout HEAD -- filename

# 完全回滚
git reset --hard HEAD
```

## 📝 推荐执行顺序

1. **创建Git分支**: `git checkout -b cleanup-project-structure`
2. **删除无用文件**: Zone.Identifier + 无价值调试文件
3. **归档测试目录**: 移动到tests/legacy/
4. **整理文档文件**: 移动到docs/reports/和docs/guides/
5. **整理调试文件**: 移动到output/debug/
6. **创建README**: 在tests/legacy/和docs/reports/创建说明
7. **测试验证**: 确认移动后文档可访问
8. **Git提交**: 提交整理变更
9. **合并分支**: 合并到主分支

## 💡 长期维护建议

1. **定期清理**: 每月清理一次临时测试目录
2. **规范命名**: 使用统一的命名约定
3. **及时归档**: 测试完成后及时归档
4. **文档分类**: 按类型存放文档（reports/guides/api）
5. **定期审查**: 每季度审查项目结构

---

**报告生成者**: Claude Code
**日期**: 2026-02-17
**推荐方案**: 方案A（彻底整理）
