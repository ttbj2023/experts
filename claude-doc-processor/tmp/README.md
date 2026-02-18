# Tmp 目录

**用途**: 临时工作目录
**状态**: ✅ 已加入允许访问的工作目录

---

## 📂 用途说明

此目录用于存放**临时性脚本和中间文件**。

---

## 🎯 使用场景

### 1. 临时脚本
```bash
# 测试某个功能时创建临时脚本
cat > tmp/test_script.sh << 'EOF'
#!/bin/bash
echo "Testing..."
EOF
chmod +x tmp/test_script.sh
./tmp/test_script.sh
```

### 2. 中间文件
```bash
# 处理过程中产生的中间文件
./convert.py document.pdf --refine-content -o tmp/intermediate/
```

### 3. 调试输出
```bash
# 调试时的临时输出
./convert.py debug.pdf -o tmp/debug/ --verbose
```

---

## 📝 与其他目录的区别

| 目录 | 用途 | Git跟踪 | 保留时间 |
|------|------|---------|---------|
| `tmp/` | 临时脚本和中间文件 | ❌ 否 | 短期（可随时删除） |
| `input/` | 待处理的输入文件 | ❌ 否 | 处理完成后可删除 |
| `output/` | 处理结果输出 | ❌ 否 | 处理完成后可删除 |
| `examples/` | 示例文档 | ✅ 是 | 永久保留 |

---

## 🧹 清理方法

```bash
# 清理所有临时文件
rm -rf tmp/*

# 或删除整个目录
rm -rf tmp/
```

---

## ⚠️ 注意事项

1. **临时性** - 此目录内容随时可能被清理
2. **不用于重要文件** - 重要文件应放在项目目录中
3. **可自动创建** - 如果不存在，可以手动创建

---

## 🔗 相关目录

- `input/` - 默认输入目录
- `output/` - 默认输出目录
- `scripts/` - 正式脚本目录

---

**维护者**: Claude Code
**最后更新**: 2026-02-18
