# Obsolete Directories 归档

**归档时间**: 2026-02-18
**原因**: 目录规范整理

---

## 📁 归档目录说明

此目录存放已被新规范替代的旧目录。

---

## 🗂️ 归档内容

### 1. input_file/ (旧的输入目录)
**替代方案**: `input/`

**原因**:
- 项目建立了标准的工作目录规范
- 使用更简洁的 `input/` 作为默认输入目录
- 旧的 `input_file/` 命名不符合新规范

**迁移指南**:
```bash
# 旧方式
cp file.pdf input_file/
./convert.py input_file/file.pdf

# 新方式
cp file.pdf input/
./convert.py input/file.pdf
```

---

### 2. intermediate/ (中间调试文件)
**替代方案**: `tmp/` 或调试时指定临时目录

**原因**:
- 调试用的中间文件应存放在临时目录
- 项目建立了 `tmp/` 作为标准临时工作目录
- 避免根目录混乱

**迁移指南**:
```bash
# 旧方式（使用intermediate/）
./convert.py test.pdf -o intermediate/debug/

# 新方式（使用tmp/）
./convert.py test.pdf -o tmp/debug/
```

---

### 3. example_output/ (示例输出 v1)
**替代方案**: `examples/` 和新的 `output/`

**原因**:
- 示例输出应该使用统一的 `output/` 目录
- 旧的示例输出已经过时
- 示例文档应放在 `examples/` 目录

---

### 4. example_output_v2/ (示例输出 v2)
**替代方案**: `examples/` 和新的 `output/`

**原因**:
- 同 example_output/
- v2版本的示例输出也已过时

---

## 📝 使用建议

### 需要这些旧目录怎么办？

如果需要使用这些旧目录中的内容，建议：

1. **查看内容**:
   ```bash
   ls archive/obsolete_directories/input_file/
   ```

2. **迁移到新目录**:
   ```bash
   # 将需要的文件迁移到新的input目录
   cp archive/obsolete_directories/input_file/*.pdf input/
   ```

3. **删除归档**（如果确认不需要）:
   ```bash
   # 谨慎操作！
   rm -rf archive/obsolete_directories/
   ```

---

## 🔗 相关目录

- **新输入目录**: `input/`
- **新输出目录**: `output/`
- **临时目录**: `tmp/`
- **示例目录**: `examples/`

---

## ⚠️ 注意事项

1. **不建议继续使用** - 这些目录已被新规范替代
2. **可以安全删除** - 如果确认不需要，可以删除整个归档
3. **先迁移再删除** - 如果需要旧目录中的文件，先迁移到新目录

---

**维护者**: Claude Code
**归档原因**: 目录规范整理 - 建立标准工作目录体系
