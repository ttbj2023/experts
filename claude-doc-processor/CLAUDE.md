# Claude Doc Processor 使用指南

**版本**: v4.0 (统一架构)
**状态**: ✅ 生产就绪
**更新**: 2026-02-18

---

## 📖 目录

- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [使用示例](#使用示例)
- [配置详解](#配置详解)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)
- [故障排查](#故障排查)

---

## 🚀 快速开始

### 5分钟上手

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥
export DEEPSEEK_API_KEY="your_deepseek_key"

# 3. 转换文档
./convert.py document.pdf -o output/
```

**就这么简单！** 输出目录包含：
- `document.md` - 最终Markdown文件
- `images/` - 提取的图片文件夹
- `meta.json` - 处理元数据

---

## 🎯 核心功能

### 统一架构（v4.0）

**核心设计理念**：
- DOCX只是PDF的前体（通过LibreOffice转换）
- PDF→MD是通用流程
- 智能PDF类型检测（文档型 vs 扫描型）

### 处理流程

```
Stage 0: DOCX→PDF预处理（可选）
Stage 1: PDF类型检测
Stage 2: 图片提取（分支选择）
Stage 3: OCR识别（GLM逐页）
Stage 3.5: 内容整理（可选）⭐
Stage 4: 图片描述（GLM）
Stage 5: 语义匹配（DeepSeek全局）
Stage 6: 智能替换（去重+清理）
```

详细架构说明请查看 [README.md](README.md)

---

## 💡 使用示例

### 基础转换

```bash
# PDF转换
./convert.py document.pdf

# DOCX转换
./convert.py document.docx -o output_dir

# 支持通配符
./convert.py docs/*.pdf --batch
```

### 高级用法

```bash
# 启用Stage 3.5内容精修（提升输出质量）
./convert.py document.pdf --refine-content

# 限制处理页数
./convert.py large_doc.pdf --max-pages 10

# 自定义配置
./convert.py document.pdf --config custom.yaml
```

---

## ⚙️ 配置详解

### 启用Stage 3.5内容精修

**方式1: 配置文件**
```yaml
# config/default.yaml
processing:
  pdf:
    enable_content_refinement: true
```

**方式2: 命令行**
```bash
./convert.py document.pdf --refine-content
```

### PDF类型检测阈值

```yaml
# config/default.yaml
detection:
  pdf:
    text_threshold: 1000    # 文档型PDF最小文本字符数
    min_text_ratio: 0.1     # 最小文本密度
```

---

## ❓ 常见问题

### Q: LibreOffice转换失败？

**解决方案**：
```bash
# 检查LibreOffice是否安装
soffice --version

# 增加超时时间
# 编辑 config/default.yaml
processing:
  docx:
    libreoffice_timeout: 120
```

### Q: Stage 5语义匹配返回0个？

**原因**：图片数量与占位符数量不匹配
**解决方案**：这是正常的，DeepSeek会智能判断，不会强行匹配

### Q: 如何提高处理速度？

**方案1**：限制页数
```bash
./convert.py large_doc.pdf --max-pages 10
```

**方案2**：禁用Stage 3.5
```yaml
processing:
  pdf:
    enable_content_refinement: false
```

---

## 🎯 最佳实践

### 1. 何时启用Stage 3.5

✅ **推荐启用**：
- 需要高质量输出
- OCR识别有较多错误
- 学术论文、技术文档

❌ **不推荐启用**：
- 快速预览
- 成本敏感项目

### 2. PDF类型选择

**文档型PDF**：
- 电子书、论文、报告
- 可以直接复制文字

**扫描型PDF**：
- 扫描件、截图PDF
- 需要OCR识别

### 3. 批量处理

```bash
# 使用--batch为每个文件创建独立目录
./convert.py docs/*.pdf --batch -o batch_output/
```

---

## 🔍 故障排查

### 诊断命令

```bash
# 1. 检查Python版本
python --version  # 需要 >= 3.8

# 2. 检查依赖安装
pip list | grep -E "PyYAML|requests|Pillow"

# 3. 测试API连通性
curl -I http://your-glm-api:9999

# 4. 测试转换（调试模式）
./convert.py input.pdf -o test/ --max-pages 1
```

### 常见错误码

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `FileNotFoundError` | 输入文件不存在 | 检查文件路径 |
| `ConnectionError` | API无法连接 | 检查网络和API地址 |
| `TimeoutError` | API响应超时 | 增加timeout配置 |
| `KeyError` | API密钥未设置 | 设置DEEPSEEK_API_KEY |

---

## 📚 更多文档

- **主文档**: [README.md](README.md) - 项目概览和架构说明
- **架构设计**: [docs/V4_ARCHITECTURE.md](docs/V4_ARCHITECTURE.md) - 详细的v4架构设计
- **完成总结**: [docs/V4_REFACTOR_COMPLETE.md](docs/V4_REFACTOR_COMPLETE.md) - v4重构完成总结

---

## 🎓 总结

### 核心要点

1. **统一入口** - 使用`./convert.py`处理所有文档
2. **智能检测** - 自动识别PDF类型并选择最优策略
3. **可选精修** - Stage 3.5提升输出质量
4. **灵活配置** - YAML + 环境变量
5. **完整日志** - 详细的处理过程记录

### 快速参考

```bash
# 基础转换
./convert.py input.pdf -o output/

# 启用内容精修
./convert.py input.pdf --refine-content

# 批量处理
./convert.py docs/*.docx --batch

# 查看帮助
./convert.py --help
```

---

**使用愉快！** 🎉

如有问题，请查阅文档或提交Issue。
