# GLM-4.6V Universal 版本快速使用指南

## 📋 基本信息

**文件名**: `process_pdf_with_glm46v_universal.py`
**版本**: Universal 1.0（通用智能布局识别版）
**适用**: 学术论文、图书、杂志、技术文档、教辅书等所有类型文档

---

## 🚀 快速开始

### 基本用法

```bash
# 处理整个PDF
python3 scripts/process_pdf_with_glm46v_universal.py /path/to/document.pdf

# 指定输出目录
python3 scripts/process_pdf_with_glm46v_universal.py document.pdf -o ./my_output

# 只处理前5页（测试效果）
python3 scripts/process_pdf_with_glm46v_universal.py document.pdf -n 5

# 从第10页开始处理
python3 scripts/process_pdf_with_glm46v_universal.py document.pdf -s 10

# 自定义API地址
python3 scripts/process_pdf_with_glm46v_universal.py document.pdf --api-url http://localhost:9999
```

### 完整参数

```bash
python3 process_pdf_with_glm46v_universal.py \
  <PDF路径> \
  -o <输出目录> \              # 默认: ./output_glm46v_universal
  -n <最大页数> \              # 默认: 全部处理
  -s <起始页码> \              # 默认: 1
  --api-url <API地址>          # 默认: http://192.168.100.110:9999
```

---

## 🎯 核心特性

### 1. 智能布局识别

自动识别并处理以下5种布局：

#### ✅ 类型1：单栏布局
- **适用**: 图书、报告、标准文档
- **处理**: 按从上到下顺序提取，保持结构

#### ✅ 类型2：等宽双栏
- **适用**: 学术论文（IEEE/ACM）、期刊
- **处理**: 使用"## 左栏内容"和"## 右栏内容"区分

#### ✅ 类型3：不等宽双栏
- **适用**: 教辅书、技术文档
- **处理**: 副栏内容转为引用块嵌入主内容

#### ✅ 类型4：图文混排
- **适用**: 杂志、画报、宣传册
- **处理**: 使用图片占位符标记位置

#### ✅ 类型5：多栏不规则
- **适用**: 报纸、复杂版式
- **处理**: 按重要性组织，保持完整性

---

## 📂 输出结构

```
output_glm46v_universal/
└── document_20250216_163800/
    ├── images/                    # PDF页面图片
    │   ├── page_001.png
    │   ├── page_002.png
    │   └── ...
    ├── page_001.md               # 单页结果（便于检查）
    ├── page_002.md
    └── document_full.md          # 完整合集
```

---

## 🔍 质量检查

处理完成后，检查以下要点：

```bash
# 1. 查看单页结果
less output_glm46v_universal/document_*/page_001.md

# 2. 检查要点
- [ ] 页眉页脚已过滤
- [ ] 布局识别正确（单栏/双栏/多栏）
- [ ] 表格格式正确（有 |---| 分隔行）
- [ ] 公式转换完整（$...$ 和 $$...$$）
- [ ] 图片有占位符（描述详细）
- [ ] 无代码块包裹正文
- [ ] 编号结构完整
```

---

## ⚙️ 性能调优

### 速度优先（快速处理）
```python
# 在脚本中修改这些参数：

# 1. 降低DPI（150 → 120）
image_paths = self.pdf_to_images(pdf_path, images_dir, max_pages, dpi=120)

# 2. 提高压缩级别
image_base64 = self.compress_image(image_path, compression="high")
```

### 质量优先（最佳效果）
```python
# 1. 提高DPI（200 → 300）
image_paths = self.pdf_to_images(pdf_path, images_dir, max_pages, dpi=300)

# 2. 降低压缩级别
image_base64 = self.compress_image(image_path, compression="low")
```

### 平衡配置（推荐）
```python
# 默认配置已是最优平衡
dpi=200
compression="low"  # 1280px, 85质量
max_tokens=65536
```

---

## 🐛 常见问题

### Q1: 布局识别错误
**A**: Universal版本依赖AI判断，如出现错误：
- 尝试使用V2版本（针对教辅书）
- 检查图片DPI是否足够（建议200+）
- 查看单页结果判断问题

### Q2: 处理速度慢
**A**: 正常速度为30-90秒/页，如需加速：
- 降低DPI（200 → 150）
- 提高压缩级别（low → high）
- 减少`max_tokens`（65536 → 32768）

### Q3: 公式转换不完整
**A**: 可能是token截断：
- 增加`max_tokens`（65536 → 131072）
- 降低图片压缩级别
- 检查原始公式是否复杂

### Q4: 表格格式错误
**A**: GLM可能遗漏分隔行：
- 检查是否有`|---|`行
- 手动添加或使用后处理脚本
- 复杂表格使用占位符

### Q5: API连接失败
**A**: 检查：
- LM Studio是否运行
- API地址是否正确（默认：http://192.168.100.110:9999）
- 端点是否为`/v1/chat/completions`
- 模型是否加载（glm-4.6v-flash）

---

## 📊 性能基准

| 文档类型 | 页数 | 处理时间 | 输出质量 |
|---------|------|----------|----------|
| 学术论文（双栏） | 10页 | ~8分钟 | ⭐⭐⭐⭐⭐ |
| 技术图书（单栏） | 20页 | ~15分钟 | ⭐⭐⭐⭐⭐ |
| 教辅书（主副栏） | 15页 | ~12分钟 | ⭐⭐⭐⭐⭐ |
| 杂志（图文混排） | 8页 | ~10分钟 | ⭐⭐⭐⭐ |

**环境**: RTX 4090, GLM-4.6V-Flash, DPI=200

---

## 🆚 与其他工具对比

| 工具 | 速度 | 质量 | 双栏支持 | 图片提取 |
|------|------|------|----------|----------|
| **Universal** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| V2 (教辅书) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ |
| PDF2MD | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⚠️ |

---

## 💡 最佳实践

### 1. 测试先行
```bash
# 总是先处理前3页测试
python3 process_pdf_with_glm46v_universal.py document.pdf -n 3
```

### 2. 质量验证
```bash
# 检查输出后再全量处理
less output_*/page_*.md
```

### 3. 批量处理
```bash
# 处理多个文档
for pdf in *.pdf; do
    python3 process_pdf_with_glm46v_universal.py "$pdf"
done
```

### 4. 后处理
```bash
# 合并多个PDF的输出
cat output_*/document_full.md > combined.md
```

---

## 📚 相关文档

- [完整版本对比](./GLM46V_VERSION_COMPARISON.md)
- [V2版本说明](./process_pdf_with_glm46v_v2.py)

---

**最后更新**: 2026-02-16
**版本**: Universal 1.0
**维护**: Claude Code Subproject Team
