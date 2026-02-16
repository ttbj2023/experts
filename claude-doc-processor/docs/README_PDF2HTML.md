# PDF → Word兼容HTML 转换工具

基于**「画框→识别→填空」**三阶段流程的自动化转换工具，将PDF文档转换为100% Microsoft Word兼容的HTML格式。

## ✨ 核心特性

- **🎯 100% Word兼容**：严格遵循HTML4.01 + CSS2.1子集，生成可直接在Word中打开编辑的HTML
- **🔬 三阶段流程**：画框（版面分析）→ 识别（内容提取）→ 填空（HTML生成）
- **🧠 本地视觉模型**：支持GLM-4.6V Flash、Qwen3VL等本地模型，无需外部API
- **📚 11类元素支持**：标题、段落、列表、公式、表格、图片、页眉页脚等
- **📐 双栏布局**：智能识别和处理中文教辅/出版物的双栏排版
- **🧮 可编辑公式**：数学公式转换为LaTeX，双击可进入Word公式编辑器
- **✅ 合规性自检**：自动检测禁用标签和属性，确保Word兼容性

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_new.txt
```

核心依赖：
- PyMuPDF - PDF处理
- Pillow - 图片处理
- requests - API调用
- PyYAML - 配置文件
- Jinja2 - 模板渲染

### 2. 准备视觉模型

本工具需要本地视觉模型支持。您可以选择以下任一方案：

**方案1：GLM-4.6V Flash（推荐）**
```bash
# 使用LM Studio运行GLM-4.6V
# 1. 下载LM Studio: https://lmstudio.ai/
# 2. 加载GLM-4.6V Flash模型
# 3. 启动API服务器（默认端口9999）
```

**方案2：Qwen3VL 8B**
```bash
# 使用Ollama运行Qwen3VL
ollama run qwen2.5-vl:8b
```

⚠️ **注意**：两个模型不能同时运行（显存限制）

### 3. 基本用法

```bash
# 处理整个PDF
python cli.py input.pdf output.html

# 处理单页（测试）
python cli.py input.pdf output.html -p 12

# 处理指定页码范围
python cli.py input.pdf output.html --pages 1-10

# 使用Qwen3VL模型
python cli.py input.pdf output.html --model qwen3vl:8b

# 保留调试文件
python cli.py input.pdf output.html --keep-debug
```

### 4. 使用Word编辑

生成的HTML文件可以直接用Microsoft Word打开：

1. 用Word 2016+打开生成的HTML文件
2. 检查格式是否正确
3. 另存为DOCX格式
4. 所有元素（文本、公式、表格）均可编辑

## 📁 项目结构

```
claude-doc-processor/
├── config/
│   ├── element_mapping.yaml      # 元素类型映射表
│   └── data_protocol.yaml        # 数据流转协议
├── templates/
│   └── word_html_templates.yaml  # HTML模板库
├── src/
│   ├── utils.py                  # 工具函数
│   ├── layout_analyzer.py        # 模块1：画框
│   ├── content_extractor.py      # 模块2：识别
│   ├── html_generator.py         # 模块3：填空
│   └── main.py                   # 主流程集成
├── cli.py                         # CLI工具
├── requirements_new.txt          # 依赖清单
├── README_PDF2HTML.md            # 本文件
├── DEVELOPMENT_PROGRESS.md       # 开发进度报告
└── docs/
    └── HTML_support_by_WORD.md   # Word兼容规范
```

## 🔧 技术架构

### 三阶段流程

```
PDF输入
  ↓
┌─────────────────────────────────────────┐
│ 阶段1：画框（版面分析）                    │
│ - PDF→高清图片（200 DPI）                 │
│ - 视觉模型识别元素框和类型                 │
│ - 输出：page_layout.json                 │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ 阶段2：识别（内容提取）                    │
│ - 裁剪元素小图                            │
│ - 视觉模型提取内容（文本/公式/表格/图片）    │
│ - 输出：page_content.json                │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ 阶段3：填空（HTML生成）                   │
│ - Jinja2模板渲染                          │
│ - 双栏布局组装                            │
│ - 合规性自检                              │
│ - 输出：final.html                       │
└─────────────────────────────────────────┘
  ↓
Word兼容HTML输出
```

### 支持的元素类型

| 元素类型 | HTML标签 | 说明 |
|---------|---------|------|
| title_h1~h6 | `<h1>`~`<h6>` | 标题1-6级 |
| paragraph | `<p>` | 正文段落 |
| ordered_list | `<ol>`+`<li>` | 有序列表 |
| unordered_list | `<ul>`+`<li>` | 无序列表 |
| formula_inline | `<script type="math/tex">` | 行内公式 |
| formula_block | `<script type="math/tex; mode=display">` | 块级公式 |
| table | `<table>` | 表格 |
| image | `<img>` (base64) | 图片 |
| caption | `<p>` | 图注/表注 |

## 📊 质量标准

- **版面识别准确率**：≥ 95%
- **内容完整性**：≥ 98%
- **公式LaTeX化准确率**：≥ 90%
- **Word兼容性**：100%（所有禁用标签/属性自动检测）

## ⚠️ 注意事项

### 模型选择
- GLM-4.6V：质量更高，适合复杂文档
- Qwen3VL：速度更快，适合简单文档
- 两者不能同时运行（显存限制）

### Word兼容性
- 严格遵循HTML4.01 + CSS2.1子集
- 禁止HTML5标签（`<section>`, `<article>`等）
- 禁止CSS3属性（`flex`, `grid`, `border-radius`等）
- 公式必须使用`<script type="math/tex">`标签
- 图片必须base64内嵌

### 性能优化
- 单页处理时间：20-40秒（取决于模型和文档复杂度）
- 建议先用单页测试效果，再批量处理
- 保留调试文件（`--keep-debug`）用于排查问题

## 🐛 故障排除

### 问题：视觉模型连接失败
```
错误: 视觉模型API调用失败
```
**解决方案**：
1. 检查LM Studio/Ollama是否运行
2. 确认端口配置（默认9999）
3. 尝试访问 http://localhost:9999/v1/models

### 问题：生成的HTML在Word中格式错乱
**解决方案**：
1. 检查是否触犯合规性警告
2. 查看 `*_validation_report.json`
3. 使用 `--keep-debug` 保留中间文件分析

### 问题：公式识别错误
**解决方案**：
1. 公式复杂度高，可手动调整LaTeX代码
2. 查看 `intermediate/page_content_*.json`
3. 修改后重新运行HTML生成模块

## 📚 相关文档

- [开发进度报告](DEVELOPMENT_PROGRESS.md) - 详细的开发计划和技术实现
- [Word兼容规范](docs/HTML_support_by_WORD.md) - 完整的技术规范说明
- [元素类型映射](config/element_mapping.yaml) - 11类元素的详细定义
- [数据流转协议](config/data_protocol.yaml) - 三阶段的JSON格式定义

## 📝 开发示例

### 测试单页处理

```bash
# 测试第12页
python cli.py "input_file/正文26春初中非常课课通数学8年级人教.pdf" \
  "output_test_page12.html" -p 12 --keep-debug
```

### 批量处理

```bash
# 处理前10页
python cli.py input.pdf output.html --pages 1-10
```

### 自定义API端点

```bash
# 使用Ollama的Qwen3VL
python cli.py input.pdf output.html \
  --api-url http://localhost:11434/v1/chat/completions \
  --model qwen2.5-vl:8b
```

## 🤝 反馈和支持

本项目处于活跃开发阶段，欢迎反馈问题和建议！

1. 查看开发进度：`DEVELOPMENT_PROGRESS.md`
2. 报告问题：请附上PDF样本和错误日志
3. 功能建议：请详细描述使用场景

## 📄 许可证

本项目为内部工具，仅供学习和研究使用。

## 🙏 致谢

- **GLM-4.6V**：智谱AI提供的视觉语言模型
- **Qwen3VL**：阿里云开源的多模态模型
- **PyMuPDF**：Artifex软件的PDF处理库
- **Jinja2**：Python模板引擎

---

**维护者**：Claude Code Subproject Team
**最后更新**：2026-02-15
**项目状态**：✅ 核心功能已完成，可用于测试
**完成度**：约90%（核心功能完成，待优化和测试）
