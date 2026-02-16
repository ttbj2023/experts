# Claude Doc Processor 使用指南

**版本**: v2.0  
**更新**: 2026-02-17  
**状态**: ✅ 生产就绪

---

## 📖 目录

- [快速开始](#快速开始)
- [安装配置](#安装配置)
- [核心功能](#核心功能)
- [使用示例](#使用示例)
- [配置详解](#配置详解)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)
- [故障排查](#故障排查)
- [进阶用法](#进阶用法)

---

## 🚀 快速开始

### 5分钟上手

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥（必需）
export DEEPSEEK_API_KEY="your_deepseek_key"

# 3. 转换PDF
./convert-pdf.py document.pdf -o output/

# 4. 查看结果
ls output/
```

**就这么简单！** 输出目录包含：
- `document.md` - 最终Markdown文件
- `images/` - 提取的图片文件夹
- `metadata.json` - 处理元数据

---

## 🔧 安装配置

### 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Linux、macOS、WSL2
- **内存**: 至少 2GB 可用内存
- **磁盘**: 至少 500MB 可用空间

### Step 1: 安装Python依赖

```bash
# 克隆项目
git clone <repository-url>
cd claude-doc-processor

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### Step 2: 安装LibreOffice（DOCX转换需要）

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

**macOS**:
```bash
brew install libreoffice
```

**Windows**:
- 下载并安装 [LibreOffice](https://www.libreoffice.org/)

### Step 3: 配置API密钥

**方式1: 环境变量（推荐）**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export DEEPSEEK_API_KEY="sk-xxxxx"
export GLM_API_KEY="your_glm_key"  # 可选

# 重新加载配置
source ~/.bashrc
```

**方式2: 临时设置**
```bash
export DEEPSEEK_API_KEY="sk-xxxxx"
./convert-pdf.py input.pdf
```

**方式3: 配置文件**
```yaml
# 编辑 config/default.yaml
models:
  deepseek:
    api_key: "sk-xxxxx"  # 不推荐，密钥会暴露
```

### Step 4: 验证安装

```bash
# 检查Python版本
python --version

# 检查LibreOffice
soffice --version

# 测试API连接
curl -I http://your-glm-api:9999
```

---

## 🎯 核心功能

### 1. PDF转Markdown

#### 基础用法

```bash
./convert-pdf.py input.pdf -o output_dir
```

#### 常用参数

```bash
# 限制处理页数
./convert-pdf.py input.pdf --max-pages 10

# 启用排版优化
./convert-pdf.py input.pdf --format-with-deepseek

# 自定义DPI（提高质量）
./convert-pdf.py input.pdf --dpi 300

# 使用自定义配置
./convert-pdf.py input.pdf --config my_config.yaml
```

#### 完整参数列表

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `input.pdf` | 输入PDF文件（必需） | - | `document.pdf` |
| `-o, --output` | 输出目录 | `output_pdf` | `-o my_output/` |
| `--config` | 配置文件路径 | `config/default.yaml` | `--config custom.yaml` |
| `--max-pages` | 最大处理页数 | 全部 | `--max-pages 10` |
| `--format-with-deepseek` | 启用排版优化 | false | `--format-with-deepseek` |
| `--dpi` | PDF渲染DPI | 200 | `--dpi 300` |
| `--glm-api-key` | GLM API密钥 | 从配置读取 | `--glm-api-key xxx` |
| `--deepseek-api-key` | DeepSeek密钥 | 从环境变量 | `--deepseek-api-key xxx` |

#### 处理流程

```
PDF文件
  ↓
1️⃣ 渲染为图片（200 DPI）
  ↓
2️⃣ GLM-4.6V-Flash OCR识别 → Markdown + 占位符
  ↓
3️⃣ DeepSeek排版优化（可选）
  ↓
4️⃣ OpenCV提取图片
  ↓
5️⃣ GLM-4.6V-Flash生成图片描述
  ↓
6️⃣ DeepSeek语义匹配（占位符↔图片）
  ↓
7️⃣ 替换占位符 → 最终Markdown
```

#### 输出结果

```
output_dir/
├── document.md              # 最终Markdown文件
├── images/                  # 提取的图片
│   ├── image_1.png
│   ├── image_2.png
│   └── ...
├── metadata.json            # 处理元数据
├── stage1_ocr.md            # 中间结果：OCR识别
├── stage1_5_formatted.md    # 中间结果：排版优化
└── image_descriptions.json  # 图片描述数据
```

---

### 2. DOCX转Markdown

#### 基础用法

```bash
./convert-docx.py input.docx -o output_dir
```

#### 常用参数

```bash
# 启用调试模式
./convert-docx.py input.docx --debug

# 自定义LibreOffice超时
./convert-docx.py input.docx --libreoffice-timeout 120

# 使用自定义GLM API地址
./convert-docx.py input.docx --glm-api-url http://api:9999
```

#### 完整参数列表

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `input.docx` | 输入DOCX文件（必需） | - | `document.docx` |
| `-o, --output` | 输出目录 | `output_docx` | `-o my_output/` |
| `--config` | 配置文件路径 | `config/default.yaml` | `--config custom.yaml` |
| `--glm-api-key` | GLM API密钥 | 从配置读取 | `--glm-api-key xxx` |
| `--deepseek-key` | DeepSeek密钥 | 从环境变量 | `--deepseek-key xxx` |
| `--glm-api-url` | GLM API地址 | 从配置读取 | `--glm-api-url http://api:9999` |
| `--libreoffice-timeout` | 转换超时（秒） | 60 | `--libreoffice-timeout 120` |
| `--debug` | 调试模式 | false | `--debug` |

#### 处理流程

```
DOCX文件
  ↓
1️⃣ LibreOffice转换为PDF
  ↓
2️⃣ GLM-4.6V-Flash OCR识别 → Markdown + 占位符
  ↓
3️⃣ GLM-4.6V-Flash生成图片描述
  ↓
4️⃣ 智能替换（去重 + 清理）
  ↓
最终Markdown
```

#### 输出结果

```
output_dir/
├── document.md              # 最终Markdown文件
├── images/                  # 提取的图片
│   ├── image_1.png
│   └── ...
├── metadata.json            # 处理元数据
├── stage2_recognized.md     # 中间结果：GLM识别
└── temp_converted.pdf       # 中间结果：转换的PDF
```

---

## 📚 使用示例

### 示例1: 转换学术论文

```bash
# 场景：转换一篇50页的PDF论文
./convert-pdf.py paper.pdf \
  --output papers/ \
  --format-with-deepseek \
  --dpi 300

# 结果：
# - 高精度公式识别
# - 表格完整保留
# - 图片自动描述
# - 标题层级规范
```

### 示例2: 批量处理技术文档

```bash
# 场景：批量转换Word技术文档
for file in docs/*.docx; do
  ./convert-docx.py "$file" \
    --output converted/ \
    --libreoffice-timeout 120
done

# 结果：
# - 批量转换所有DOCX文件
# - 保留原始表格结构
# - 公式正确转换
```

### 示例3: 快速预览（限制页数）

```bash
# 场景：快速查看前10页内容
./convert-pdf.py large_book.pdf \
  --max-pages 10 \
  --output preview/

# 适用场景：
# - 评估转换质量
# - 快速获取摘要
# - 节省API调用
```

### 示例4: 扫描版PDF处理

```bash
# 场景：处理扫描版教材（提高DPI）
./convert-pdf.py scanned_textbook.pdf \
  --dpi 300 \
  --format-with-deepseek \
  --output textbook/

# 结果：
# - 高清渲染提升OCR准确率
# - 自动优化排版
# - 公式和图表清晰识别
```

### 示例5: 调试模式排查问题

```bash
# DOCX转换调试
./convert-docx.py document.docx \
  --debug \
  --output debug_output/

# 保留所有中间结果：
# - temp_converted.pdf (LibreOffice转换结果)
# - stage2_recognized.md (GLM识别结果)
# - 详细日志输出
```

---

## ⚙️ 配置详解

### 配置文件结构

主配置文件：`config/default.yaml`

```yaml
# ====================
# 模型配置
# ====================
models:
  glm:
    api_url: "http://192.168.100.110:9999"  # GLM API地址
    model: "zai-org/glm-4.6v-flash"        # 模型名称
    max_tokens: 8192                        # 最大token数
    timeout: 60                             # 超时时间（秒）
    temperature: 0.3                        # 温度参数

  deepseek:
    api_key: "${DEEPSEEK_API_KEY}"         # 从环境变量读取
    model: "deepseek-chat"                  # 模型名称
    timeout: 120                            # 超时时间（秒）
    temperature: 0.1                        # 温度参数
    max_tokens: 4000                        # 最大token数

# ====================
# 处理配置
# ====================
processing:
  pdf:
    dpi: 200                                # 渲染DPI
    max_pages: null                         # 最大页数（null=全部）
    opencv_min_area: 0.02                   # 最小图片面积比例
    opencv_padding: 10                      # 边界框扩展像素
    enable_formatting: false                # 启用排版优化

  docx:
    libreoffice_timeout: 60                 # LibreOffice超时
    image_max_size: 1280                    # 图片最大尺寸
    document_chunk_size: 64000              # 文档分段阈值
    image_quality: 85                       # JPEG压缩质量
    enable_code_block_cleanup: true         # 代码块清理
    enable_separator_cleanup: true          # 分隔符清理
    enable_duplicate_detection: true        # 重复检测

# ====================
# 输出配置
# ====================
output:
  default_dir: "output"                     # 默认输出目录
  save_intermediate: true                   # 保存中间结果
  log_level: "INFO"                         # 日志级别
  log_format: "%(asctime)s - %(levelname)s - %(message)s"

# ====================
# 图片提取配置
# ====================
image_extraction:
  method: "auto"                            # 提取方法：auto/opencv/docx
  formats: ["png", "jpg", "jpeg"]           # 保存格式
  extract_all: true                         # 提取所有图片
  min_width: 50                             # 最小宽度（像素）
  min_height: 50                            # 最小高度（像素）

# ====================
# OCR提示词模板
# ====================
prompts:
  ocr: |
    你是一个专业的OCR识别系统...
  
  image_description: |
    请详细描述这张图片的内容...
  
  semantic_matching: |
    你是一个智能文档处理助手...
  
  markdown_formatting: |
    你是一个专业的Markdown排版专家...
```

### 环境变量

```bash
# 必需：DeepSeek API密钥
export DEEPSEEK_API_KEY="sk-xxxxx"

# 可选：GLM API密钥（如果配置文件未设置）
export GLM_API_KEY="your_glm_key"

# 可选：自定义配置文件路径
export CLAUDE_DOC_CONFIG="/path/to/config.yaml"

# 可选：自定义日志级别
export CLAUDE_DOC_LOG_LEVEL="DEBUG"
```

### 配置优先级

```
命令行参数 > 环境变量 > YAML配置文件 > 默认值
```

**示例**：
```bash
# YAML配置: dpi: 200
# 环境变量: 未设置
# 命令行: --dpi 300
# 实际使用: 300 ✅
```

---

## ❓ 常见问题

### Q1: LibreOffice转换失败怎么办？

**错误信息**：
```
LibreOffice conversion failed: timeout
```

**解决方案**：

1. **检查LibreOffice是否安装**
   ```bash
   soffice --version
   ```

2. **增加超时时间**
   ```bash
   ./convert-docx.py input.docx --libreoffice-timeout 120
   ```

3. **手动转换测试**
   ```bash
   soffice --headless --convert-to pdf input.docx
   ```

4. **重新安装LibreOffice**
   ```bash
   sudo apt-get install --reinstall libreoffice
   ```

---

### Q2: GLM API连接超时

**错误信息**：
```
GLM API connection timeout
```

**解决方案**：

1. **检查API地址**
   ```bash
   curl http://your-glm-api:9999
   ```

2. **检查网络连接**
   ```bash
   ping your-glm-api
   ```

3. **增加超时时间**
   ```bash
   # 编辑 config/default.yaml
   models:
     glm:
       timeout: 120  # 增加到120秒
   ```

4. **使用命令行覆盖**
   ```bash
   ./convert-pdf.py input.pdf --glm-api-url http://new-api:9999
   ```

---

### Q3: DeepSeek API密钥无效

**错误信息**：
```
DeepSeek API error: Invalid API key
```

**解决方案**：

1. **验证环境变量**
   ```bash
   echo $DEEPSEEK_API_KEY
   ```

2. **重新设置密钥**
   ```bash
   export DEEPSEEK_API_KEY="sk-xxxxx"
   ```

3. **添加到 ~/.bashrc**
   ```bash
   echo 'export DEEPSEEK_API_KEY="sk-xxxxx"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **使用命令行传递**
   ```bash
   ./convert-pdf.py input.pdf --deepseek-api-key sk-xxxxx
   ```

---

### Q4: 图片提取不完整

**症状**：某些图片没有被提取

**解决方案**：

1. **提高DPI**
   ```bash
   ./convert-pdf.py input.pdf --dpi 300
   ```

2. **禁用OpenCV，使用完整提取**
   ```yaml
   # 编辑 config/default.yaml
   image_extraction:
     method: "docx"  # 或 "pdf" (完整提取)
   ```

3. **调整检测参数**
   ```yaml
   processing:
     pdf:
       opencv_min_area: 0.01  # 降低阈值
       opencv_padding: 20     # 增加边界
   ```

4. **检查中间结果**
   ```bash
   # 查看 metadata.json 中的图片列表
   cat output/metadata.json | jq '.images'
   ```

---

### Q5: 处理速度太慢

**症状**：转换一个50页PDF需要很长时间

**优化方案**：

1. **限制处理页数**
   ```bash
   ./convert-pdf.py input.pdf --max-pages 10
   ```

2. **禁用排版优化**
   ```yaml
   processing:
     pdf:
       enable_formatting: false
   ```

3. **降低DPI**
   ```bash
   ./convert-pdf.py input.pdf --dpi 150
   ```

4. **使用更快的API**
   ```yaml
   models:
     glm:
       timeout: 30  # 减少超时时间
   ```

---

## 💡 最佳实践

### 1. 配置管理

**✅ 推荐**：
```bash
# 使用环境变量管理密钥
export DEEPSEEK_API_KEY="sk-xxxxx"

# 创建自定义配置文件
cp config/default.yaml config/my_config.yaml
vim config/my_config.yaml

# 使用自定义配置
./convert-pdf.py input.pdf --config config/my_config.yaml
```

**❌ 不推荐**：
```bash
# 在配置文件中硬编码密钥
vim config/default.yaml
# api_key: "sk-xxxxx"  # 不安全！
```

---

### 2. 批量处理

**✅ 推荐**：
```bash
# 使用脚本批量处理
#!/bin/bash
for file in input/*.pdf; do
  output="output/$(basename "$file" .pdf)"
  ./convert-pdf.py "$file" -o "$output"
done
```

**✅ 推荐**：
```bash
# 使用GNU parallel（更高效）
find input/ -name "*.pdf" | \
  parallel -j 4 ./convert-pdf.py {} -o output/{/}
```

---

### 3. 质量控制

**✅ 推荐工作流**：

```bash
# Step 1: 先转换前5页测试质量
./convert-pdf.py large_doc.pdf --max-pages 5 -o test/

# Step 2: 检查输出质量
cat test/large_doc.md | head -100

# Step 3: 调整配置
vim config/default.yaml

# Step 4: 完整转换
./convert-pdf.py large_doc.pdf -o final/
```

---

### 4. 错误处理

**✅ 推荐**：
```bash
# 使用set -e捕获错误
#!/bin/bash
set -e

./convert-pdf.py input.pdf -o output/ || {
  echo "转换失败，检查日志"
  cat output/*.log
  exit 1
}
```

---

### 5. 资源管理

**✅ 推荐**：
```bash
# 清理中间结果节省空间
./convert-pdf.py input.pdf -o output/
rm output/stage*.md  # 删除中间文件

# 或直接禁用保存中间结果
vim config/default.yaml
# output:
#   save_intermediate: false
```

---

## 🔍 故障排查

### 诊断命令

```bash
# 1. 检查Python版本
python --version  # 需要 >= 3.8

# 2. 检查依赖安装
pip list | grep -E "PyYAML|requests|Pillow|python-docx|PyMuPDF|opencv"

# 3. 检查LibreOffice
soffice --version

# 4. 测试API连通性
curl -I http://your-glm-api:9999
curl -I https://api.deepseek.com

# 5. 检查环境变量
echo $DEEPSEEK_API_KEY
echo $GLM_API_KEY

# 6. 测试转换（调试模式）
./convert-pdf.py input.pdf -o test/ --max-pages 1
```

### 日志分析

```bash
# 查看详细日志
./convert-pdf.py input.pdf -o output/ 2>&1 | tee conversion.log

# 搜索错误
grep -i "error" conversion.log
grep -i "failed" conversion.log
grep -i "timeout" conversion.log
```

### 常见错误码

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `FileNotFoundError` | 输入文件不存在 | 检查文件路径 |
| `PermissionError` | 无写入权限 | 检查输出目录权限 |
| `ConnectionError` | API无法连接 | 检查网络和API地址 |
| `TimeoutError` | API响应超时 | 增加timeout配置 |
| `KeyError` | API密钥未设置 | 设置DEEPSEEK_API_KEY |

---

## 🚀 进阶用法

### 1. 自定义OCR提示词

```yaml
# 编辑 config/default.yaml
prompts:
  ocr: |
    你是一个专业的OCR系统。
    
    特殊要求：
    - 保留所有数字和单位
    - 识别表格并使用Markdown表格语法
    - 公式使用LaTeX语法：$$x^2$$
    
    请识别以下图片内容：
```

### 2. 添加新的转换器

```python
# 创建 src/converters/html_converter.py
from .base import BaseConverter

class HTMLConverter(BaseConverter):
    def convert(self, input_path: str, output_dir: str):
        # 实现HTML转换逻辑
        pass
```

### 3. 集成到自动化流程

```python
# 在Python脚本中使用
from src.converters.pdf_converter import PDFConverter

converter = PDFConverter(config_path='config/default.yaml')
result = converter.convert('input.pdf', 'output/')
print(f"转换完成: {result['output_file']}")
```

### 4. 监控处理进度

```bash
# 使用watch监控输出目录
watch -n 5 'ls -lh output/'

# 监控日志文件
tail -f output/conversion.log
```

---

## 📞 获取帮助

### 文档资源

- **主文档**: [README.md](README.md) - 项目概览
- **重构计划**: [docs/REFACTOR_PLAN.md](docs/REFACTOR_PLAN.md) - 架构说明
- **Scripts说明**: [scripts/README.md](scripts/README.md) - 核心脚本参考

### 问题反馈

1. **查看日志**: 检查输出目录的日志文件
2. **启用调试**: 使用 `--debug` 参数
3. **查阅文档**: 阅读相关章节
4. **提交Issue**: 在GitHub提交问题

---

## 🎓 总结

### 核心要点

1. **安装简单** - 一条命令安装依赖
2. **配置灵活** - YAML + 环境变量
3. **使用便捷** - 命令行接口清晰
4. **功能强大** - AI驱动的智能处理
5. **文档完整** - 详细的使用指南

### 快速参考

```bash
# PDF转换
./convert-pdf.py input.pdf -o output/

# DOCX转换
./convert-docx.py input.docx -o output/

# 配置密钥
export DEEPSEEK_API_KEY="sk-xxxxx"

# 查看帮助
./convert-pdf.py --help
./convert-docx.py --help
```

---

**祝使用愉快！** 🎉

如有问题，请查阅文档或提交Issue。
