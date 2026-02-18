# Obsolete Files 归档

**归档时间**: 2026-02-18
**原因**: 根目录清理

---

## 📁 归档文件说明

此目录存放项目开发过程中的临时报告和调试文件。

---

## 🗂️ 归档文件清单

### 1. CHANGELOG.md
**类型**: 项目变更日志

**原因**:
- 项目没有正式维护CHANGELOG
- 此文件内容可能是临时记录
- 版本历史应该通过Git查看

**替代方案**:
```bash
# 查看项目历史
git log --oneline

# 查看版本标签
git tag
```

---

### 2. CORE_SCRIPTS_ANALYSIS.md
**类型**: 核心脚本分析报告

**原因**:
- 临时性的分析报告
- 已完成v4.0重构，分析报告已过时
- 相关文档应放在 `docs/reports/` 目录

**相关文档**:
- `docs/V4_ARCHITECTURE.md` - v4.0架构设计
- `docs/V4_REFACTOR_COMPLETE.md` - v4.0重构完成总结

---

### 3. GLM_OPTIMIZATION_REPORT.md
**类型**: GLM模型优化报告

**原因**:
- 临时性的优化测试报告
- 已集成到正式文档中
- 相关文档应放在 `docs/reports/` 目录

**相关文档**:
- `docs/reports/GLM46V_PROCESSING_REPORT.md` - GLM-4.6V处理报告

---

### 4. debug_parser_test.py
**类型**: 调试脚本

**原因**:
- 临时调试脚本
- 已完成调试，不再需要
- 调试脚本应放在 `tmp/` 或 `scripts/` 目录

**替代方案**:
```bash
# 新的调试脚本应放在tmp/
vim tmp/debug_test.py

# 或放在scripts/
vim scripts/debug_tool.py
```

---

## 📝 使用建议

### 需要这些文件怎么办？

1. **查看内容**:
   ```bash
   cat archive/obsolete_files/CORE_SCRIPTS_ANALYSIS.md
   ```

2. **迁移到合适位置**（如果仍需要）:
   ```bash
   # 报告类文件迁移到docs/reports/
   mv archive/obsolete_files/GLM_OPTIMIZATION_REPORT.md docs/reports/

   # 脚本类文件迁移到scripts/
   mv archive/obsolete_files/debug_parser_test.py scripts/
   ```

3. **删除归档**（如果确认不需要）:
   ```bash
   # 谨慎操作！
   rm -rf archive/obsolete_files/
   ```

---

## 🔗 相关目录

- **项目文档**: `docs/`
- **报告文档**: `docs/reports/`
- **脚本目录**: `scripts/`
- **临时目录**: `tmp/`

---

## ⚠️ 注意事项

1. **不建议继续使用** - 这些是临时文件，已不再维护
2. **可以安全删除** - 如果确认不需要，可以删除整个归档
3. **重要内容迁移** - 如果有重要信息，先迁移到合适的位置

---

## 📖 文件组织规范

根据项目规范，不同类型的文件应放在：

| 文件类型 | 应放位置 | 示例 |
|---------|---------|------|
| 项目文档 | `docs/` | README.md, ARCHITECTURE.md |
| 研究报告 | `docs/reports/` | GLM46V_PROCESSING_REPORT.md |
| 脚本工具 | `scripts/` | ai_workflow_example.sh |
| 临时脚本 | `tmp/` | debug_test.py |
| 示例文件 | `examples/` | academic_paper.md |
| 配置文件 | `config/` | default.yaml |

---

**维护者**: Claude Code
**归档原因**: 根目录清理 - 移除临时文件和非标准文件
