# PDF转HTML快速参考指南

## 一分钟决策树

```
开始
  │
  ├─ 需要最高质量？
  │   └─ 是 → GLM-4.6V方案 ⭐⭐⭐⭐⭐
  │
  └─ 需要快速预览？
      └─ 是 → pdf2htmlEX ⭐⭐⭐⭐
```

## 三行代码解决方案

### 方案1: GLM-4.6V（推荐）

```bash
# PDF → Markdown → HTML
python3 scripts/process_pdf_with_glm46v_v2.py "input.pdf" -o output
python3 scripts/convert_md_to_html_enhanced.py output/xxx.md output.html
# 用Word打开output.html，另存为DOCX
```

**优点**: 质量最高 | **缺点**: 较慢(20秒/页) | **适用**: 复杂数学教材

---

### 方案2: pdf2htmlEX（快速）

```bash
# 安装（一次性）
sudo apt-get install pdf2htmlex

# 直接转换
pdf2htmlEX --zoom 1.5 input.pdf output.html
```

**优点**: 快速 | **缺点**: 公式非LaTeX | **适用**: 快速预览

---

## 关键对比表

| 需求 | 推荐方案 | 理由 |
|------|----------|------|
| **数学公式完美** | GLM-4.6V | LaTeX→MathJax |
| **双栏布局** | GLM-4.6V | AI智能理解 |
| **快速预览** | pdf2htmlEX | 秒级处理 |
| **Word编辑** | GLM-4.6V | 标准HTML |
| **表格保留** | GLM-4.6V | 识别准确 |

## 常见问题

### Q1: 哪个方案最好？
**A**: GLM-4.6V质量最高，适合复杂文档。pdf2htmlEX速度快，适合快速预览。

### Q2: 能否直接输出HTML？
**A**:
- ✅ GLM-4.6V: 可以（修改prompt）
- ✅ pdf2htmlEX: 可以（原生支持）

### Q3: 如何保留数学公式？
**A**: 使用GLM-4.6V，输出LaTeX格式，用MathJax渲染：
```html
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

### Q4: 输出能在Word中编辑吗？
**A**:
- ✅ GLM-4.6V → 自定义HTML: 完美兼容
- ⚠️ pdf2htmlEX: 基本兼容
- ❌ pdftohtml: 不兼容

### Q5: 处理速度对比？
| 方案 | 1页时间 | 10页时间 |
|------|---------|----------|
| GLM-4.6V | 20秒 | 3.3分钟 |
| pdf2htmlEX | 5秒 | 50秒 |
| pdftohtml | 2秒 | 20秒 |

### Q6: 成本对比？
| 方案 | 成本 |
|------|------|
| GLM-4.6V | API调用费（约¥0.01/页） |
| pdf2htmlEX | 免费 |
| pdftohtml | 免费 |

## 实施清单

### 立即开始（GLM-4.6V）
- [ ] 测试`process_pdf_with_glm46v_v2.py`
- [ ] 测试`convert_md_to_html_enhanced.py`
- [ ] 处理1-2页样本
- [ ] 检查输出质量
- [ ] 优化prompt（可选）

### 一个月内（优化）
- [ ] 开发自动选择逻辑
- [ ] 实现缓存机制
- [ ] 批量处理优化
- [ ] A/B测试
- [ ] 文档和培训

## 快速命令速查

```bash
# GLM-4.6V: 处理PDF（指定页数）
python3 scripts/process_pdf_with_glm46v_v2.py input.pdf -o output -n 5 -s 1

# GLM-4.6V: 处理整个PDF
python3 scripts/process_pdf_with_glm46v_v2.py input.pdf -o output

# Markdown转HTML
python3 scripts/convert_md_to_html_enhanced.py input.md output.html

# pdf2htmlEX: 快速转换
pdf2htmlEX --zoom 1.5 input.pdf output.html

# pdftohtml: 快速预览
pdftohtml -c -s -noframes input.pdf output.html
```

## 质量检查清单

转换完成后，检查：
- [ ] 表格结构完整（列数正确）
- [ ] 数学公式显示正常（LaTeX渲染）
- [ ] 双栏布局合理（主内容+注释）
- [ ] 页眉页脚已删除
- [ ] 标题层级正确（# ## ###）
- [ ] 中文显示正常（无乱码）
- [ ] 在Word中可打开和编辑
- [ ] 图片清晰度和位置正确

## 推荐工作流

### 完美质量工作流
```
1. GLM-4.6V处理 → Markdown
2. 人工检查和修正（可选）
3. 转换为HTML
4. Word打开并编辑
5. 另存为DOCX
```

### 批量处理工作流
```
1. GLM-4.6V批量处理 → Markdown
2. 自动转换HTML
3. 抽检10%质量
4. Word批量编辑
5. 输出DOCX
```

### 快速预览工作流
```
1. pdf2htmlEX快速转换
2. 浏览器查看
3. 确认内容正确
4. GLM-4.6V重新处理（如需高质量）
```

## 联系和支持

- **完整报告**: `PDF2HTML_RESEARCH_REPORT.md`
- **代码示例**: `scripts/`
- **测试样本**: `input_file/`
- **问题反馈**: 创建GitHub Issue

---

**最后更新**: 2026-02-15
**版本**: 1.0
