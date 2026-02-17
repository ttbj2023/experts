# Output 目录

本目录用于存放所有测试、转换和临时生成的输出文件。

## 📂 目录结构

```
output/
├── 手册相关输出（6个）
│   ├── 手册答案26春初中非常课课通数学8年级人教/
│   ├── 手册答案26春初中非常课课通数学8年级人教.md
│   ├── 手册正文26春初中非常课课通数学8年级人教/
│   ├── 手册正文26春初中非常课课通数学8年级人教.md
│   ├── 正文26春初中非常课课通数学8年级人教/
│   └── 正文26春初中非常课课通数学8年级人教.md
│
├── output_* 测试输出（85个）
│   ├── output_docx_to_md*/          # DOCX转换测试
│   ├── output_glm46v*/              # GLM-4.6V模型测试
│   ├── output_v3*/                  # v3版本测试
│   ├── output_test*/                # 各种功能测试
│   └── ...                          # 其他测试输出
│
└── README.md                        # 本文件
```

## 📊 统计信息

- **总目录/文件数**: 91个
- **手册相关**: 6个
- **测试输出**: 85个

## 🏷️ 主要分类

### 1. 版本测试输出
- `output_docx_to_md*`: v1版本转换输出
- `output_docx_to_md_v2*`: v2版本转换输出
- `output_v3*`: v3版本（当前版本）测试输出

### 2. 模型测试输出
- `output_glm46v*`: GLM-4.6V模型各种参数测试
- `output_glm*`: GLM模型其他版本测试
- `output_zai_model`: Zai模型测试

### 3. 功能测试输出
- `output_test*`: 各种功能测试
  - `output_test_complete`: 完整流程测试
  - `output_test_extract_images`: 图片提取测试
  - `output_test_placeholder`: 占位符测试
  - `output_test_v*`: 各版本功能测试

### 4. 参数优化测试
- `output_1024px_test`, `output_1280px_test`: 图片尺寸测试
- `output_enhanced_prompt`: 增强提示词测试
- `output_no_filter`, `output_no_separator`: 参数配置测试

### 5. 文档处理输出
- `output_tea_book*`: 教材相关文档处理
- `output_pdf*`: PDF处理测试
- `output_3pages_demo`, `output_5pages*`: 分页处理测试

## 🧹 清理建议

### 可以安全删除的测试
- 所有 `output_test_*` 目录（功能测试完成）
- 重复版本的输出（保留最新版本即可）
- 参数优化测试（已确定最优参数）

### 建议保留的输出
- 最新版本的完整输出（`output_v3_final*`）
- 重要的文档处理结果（手册相关）
- 有参考价值的对比测试

## ⚠️ 注意事项

1. **不纳入版本控制**: 本目录内容不应提交到Git
2. **定期清理**: 建议定期清理过期的测试输出
3. **重要输出备份**: 有价值的输出应移到专门的项目目录
4. **磁盘空间**: 注意监控本目录占用的磁盘空间

## 📝 使用说明

### 查找特定输出
```bash
# 查找v3版本的所有输出
ls output/output_v3*

# 查找最新的测试输出
ls -lt output/output_test* | head -10

# 查找GLM模型测试
ls output/output_glm*
```

### 清理旧输出
```bash
# 删除所有测试输出（谨慎使用！）
rm -rf output/output_test_*

# 删除特定版本的输出
rm -rf output/output_v2_*

# 查看目录占用空间
du -sh output/output_*
```

### 批量处理输出
```bash
# 统计各类型输出数量
ls output/ | grep -c "output_v3"
ls output/ | grep -c "output_test"
ls output/ | grep -c "output_glm"
```

## 🔗 相关目录

- `input_file/`: 输入文件目录
- `archive/legacy/`: 归档脚本目录
- `scripts/`: 转换脚本目录

---

**创建时间**: 2026-02-17
**整理人**: Claude Code
**版本**: 1.0.0
