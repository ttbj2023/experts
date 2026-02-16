# 脚本归档清理建议报告

生成时间：2026-02-17
项目：claude-doc-processor

## 📊 脚本清单统计

### 总览
- **总脚本数**: 10个转换脚本
- **总大小**: 367.6KB
- **主要类别**: DOCX转换、PDF转换、其他格式转换

---

## 🗂️ 详细分类

### 一、DOCX转换脚本（3个）

| 文件名 | 大小 | 版本 | 状态 | 建议 |
|--------|------|------|------|------|
| `convert_docx_to_markdown.py` | 20K | v1.0 | ⚠️ 旧版本 | 📦 **归档** |
| `convert_docx_to_markdown_v2.py` | 48K | v2.0 | ⚠️ 旧版本 | 📦 **归档** |
| `convert_docx_to_markdown_v3.py` | 47K | v3.0 | ✅ **当前版本** | 🟢 **保留** |

#### 功能对比
- **v1.0**: 基础DOCX转换，简单的图片提取和公式转换
- **v2.0**: 引入图片占位符机制（通用文档版）
- **v3.0**: 三阶段架构，GLM-4.6V-Flash + DeepSeek语义匹配，100%匹配率

#### 建议
- ✅ **保留**: v3版本（当前使用）
- 📦 **归档**: v1和v2版本到 `archive/legacy/converters/`

---

### 二、PDF转换脚本（4个）

| 文件名 | 大小 | 功能 | 状态 | 建议 |
|--------|------|------|------|------|
| `convert_pdf_to_markdown_with_images.py` | 57K | PDF智能分类转换 | ⚠️ 功能重复 | 📦 **归档** |
| `convert_pdf_to_markdown_with_images_backup.py` | 57K | 同上（备份） | ❌ 冗余备份 | 🗑️ **删除** |
| `convert_pdf_complete.py` | 35K | PDF完整版（5阶段） | ⚠️ 早期实验性 | 📦 **归档** |
| `convert_pdftotext_to_md.py` | 5.5K | PDF文本转MD | ⚠️ 功能单一 | 📦 **归档** |

#### 功能说明
1. **convert_pdf_to_markdown_with_images.py**:
   - 智能分类版本
   - 文字PDF：直接提取嵌入图片
   - 扫描件PDF：GLM-4.6V-Flash识别裁剪
   - **问题**: 与DOCX v3功能重叠

2. **convert_pdf_to_markdown_with_images_backup.py**:
   - 完全相同的备份文件
   - **建议**: 直接删除

3. **convert_pdf_complete.py**:
   - 早期5阶段架构：GLM-4.6V-Flash + OpenCV + GLM-4V + DeepSeek
   - **问题**: 实验性质，已被v3架构替代

4. **convert_pdftotext_to_md.py**:
   - 简单的pdftotext输出转换
   - **问题**: 功能单一，使用场景有限

#### 建议
- 📦 **归档**到 `archive/legacy/pdf_converters/`:
  - convert_pdf_to_markdown_with_images.py
  - convert_pdf_complete.py
  - convert_pdftotext_to_md.py
- 🗑️ **直接删除**: convert_pdf_to_markdown_with_images_backup.py

---

### 三、其他转换脚本（3个）

| 文件名 | 大小 | 功能 | 状态 | 建议 |
|--------|------|------|------|------|
| `convert_md_to_docx.py` | 8.1K | MD→DOCX | ✅ 独立功能 | 🟡 **评估后保留** |
| `convert_md_to_docx_enhanced.py` | 12K | MD→DOCX增强版 | ⚠️ 重复功能 | 📦 **归档** |
| `convert_md_to_word_with_formulas.py` | 5.6K | MD→Word（公式） | ⚠️ 重复功能 | 📦 **归档** |
| `convert_md_to_html_enhanced.py` | 18K | MD→HTML增强版 | ✅ 独立功能 | 🟡 **评估后保留** |

#### 功能对比
- **convert_md_to_docx.py**: 基础MD到DOCX转换
- **convert_md_to_docx_enhanced.py**: 增强版（功能重叠）
- **convert_md_to_word_with_formulas.py**: 专门处理公式（功能重叠）
- **convert_md_to_html_enhanced.py**: MD到HTML转换

#### 建议
- 🟢 **保留**: 基础版（功能最简洁）
  - convert_md_to_docx.py
  - convert_md_to_html_enhanced.py
- 📦 **归档**: 功能重复或专项版本
  - convert_md_to_docx_enhanced.py
  - convert_md_to_word_with_formulas.py

---

## 📋 清理行动计划

### 阶段1：创建归档目录结构

```bash
mkdir -p archive/legacy/converters
mkdir -p archive/legacy/pdf_converters
mkdir -p archive/legacy/md_converters
```

### 阶段2：归档旧版本（共7个文件）

#### DOCX旧版本（2个）
```bash
mv scripts/convert_docx_to_markdown.py archive/legacy/converters/
mv scripts/convert_docx_to_markdown_v2.py archive/legacy/converters/
```

#### PDF转换脚本（3个）
```bash
mv scripts/convert_pdf_to_markdown_with_images.py archive/legacy/pdf_converters/
mv scripts/convert_pdf_complete.py archive/legacy/pdf_converters/
mv scripts/convert_pdftotext_to_md.py archive/legacy/pdf_converters/
```

#### MD转换脚本（2个）
```bash
mv scripts/convert_md_to_docx_enhanced.py archive/legacy/md_converters/
mv scripts/convert_md_to_word_with_formulas.py archive/legacy/md_converters/
```

### 阶段3：删除冗余文件（共1个）

```bash
rm scripts/convert_pdf_to_markdown_with_images_backup.py
```

### 阶段4：创建归档说明文件

创建 `archive/legacy/README.md` 记录：
- 归档时间
- 文件清单
- 归档原因
- 功能简要说明

---

## ✅ 清理后的结果

### 保留的脚本（4个）

| 文件名 | 功能 | 用途 |
|--------|------|------|
| `convert_docx_to_markdown_v3.py` | DOCX→MD（三阶段） | **主力脚本** |
| `convert_md_to_docx.py` | MD→DOCX | Markdown反向转换 |
| `convert_md_to_html_enhanced.py` | MD→HTML | HTML生成 |
| `README_convert_docx_to_markdown_v3.md` | v3文档 | 使用说明 |

### 归档的脚本（7个）

存放在 `archive/legacy/` 相应子目录中，按类别组织。

### 删除的脚本（1个）

`convert_pdf_to_markdown_with_images_backup.py` - 完全重复的备份文件

---

## 📈 清理收益

- ✅ **脚本数量**: 10个 → 4个（减少60%）
- ✅ **代码体积**: 367.6KB → ~80KB（减少78%）
- ✅ **维护复杂度**: 大幅降低
- ✅ **功能清晰度**: 显著提升
- ✅ **历史保留**: 所有旧版本安全归档

---

## ⚠️ 注意事项

1. **备份优先**: 执行清理前先创建完整备份
2. **测试验证**: 清理后测试主力脚本功能正常
3. **文档更新**: 更新项目README说明当前使用的脚本
4. **Git提交**: 归档操作单独提交，便于回溯

---

## 🎯 执行建议

### 推荐执行顺序

1. **准备阶段**（安全）
   - 创建Git分支：`git checkout -b cleanup-legacy-scripts`
   - 创建归档目录结构

2. **归档阶段**（可逆）
   - 移动文件到archive目录
   - 创建归档README
   - Git提交归档变更

3. **测试阶段**（验证）
   - 测试convert_docx_to_markdown_v3.py功能
   - 确认所有依赖正常

4. **清理阶段**（最终）
   - 删除冗余备份文件
   - 更新项目文档
   - 最终Git提交

5. **合并阶段**（完成）
   - 合并分支到主分支
   - 删除临时分支

---

**报告生成者**: Claude Code
**日期**: 2026-02-17
