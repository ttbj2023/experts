# DOCX to Markdown 转换工具使用文档

## 概述

本工具用于将DOCX文件批量转换为Markdown格式，特别适用于包含数学公式和图片的文档（如数学试卷、教材等）。

### 核心功能

- ✅ **图片提取**: 自动提取DOCX中的图片到独立目录
- ✅ **图片压缩**: 使用pngquant压缩图片，节省73%-78%空间
- ✅ **公式转换**: 支持OMML格式数学公式转换为LaTeX
- ✅ **批量处理**: 支持批量转换多个DOCX文件
- ✅ **相对路径**: 图片使用相对路径引用，便于迁移
- ✅ **详细日志**: 生成转换日志和统计信息

## 系统要求

### 必需工具

- **Python 3.7+**
- **LibreOffice** (用于DOCX转HTML和图片提取)
- **pngquant** (用于图片压缩)

### Python依赖

```bash
pip install python-docx latex2mathml
```

### 系统工具安装

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice pngquant

# 其他系统请参考官方文档
```

## 项目结构

```
scripts/
├── convert_docx_to_markdown.py    # 主转换脚本
├── batch_convert_docx_to_md.sh    # 批量处理脚本
├── utils/
│   ├── omml_converter.py          # OMML公式转LaTeX工具
│   └── image_optimizer.py         # 图片压缩工具
└── DOCX_TO_MARKDOWN_README.md     # 本文档

input_file/                         # 输入DOCX文件目录
└── *.docx

output_docx_to_md/                  # 输出目录
├── 文件名/
│   ├── document.md                # 转换后的Markdown
│   ├── images/                    # 提取的图片
│   └── meta.json                  # 元数据
└── conversion_log.md              # 批量转换日志
```

## 使用方法

### 1. 单个文件转换

#### 基本用法

```bash
python3 scripts/convert_docx_to_markdown.py input.docx
```

#### 指定输出目录

```bash
python3 scripts/convert_docx_to_markdown.py input.docx -o my_output_dir
```

#### 不压缩图片

```bash
python3 scripts/convert_docx_to_markdown.py input.docx --no-optimize
```

#### 自定义图片质量

```bash
# 质量范围: 1-100，默认85
python3 scripts/convert_docx_to_markdown.py input.docx --quality 90
```

#### 完整示例

```bash
python3 scripts/convert_docx_to_markdown.py \
    "input_file/2025年江苏省南京市中考数学试卷.docx" \
    -o output_docx_to_md \
    --quality 85
```

### 2. 批量文件转换

#### 基本用法

```bash
./scripts/batch_convert_docx_to_md.sh
```

#### 自定义输入输出目录

```bash
INPUT_DIR=/path/to/docx \
OUTPUT_DIR=/path/to/output \
./scripts/batch_convert_docx_to_md.sh
```

#### 自定义图片质量

```bash
IMAGE_QUALITY=90 \
./scripts/batch_convert_docx_to_md.sh
```

#### 禁用图片优化

```bash
OPTIMIZE_IMAGES=false \
./scripts/batch_convert_docx_to_md.sh
```

### 3. Python API使用

```python
from convert_docx_to_markdown import DocxToMarkdownConverter

# 创建转换器
converter = DocxToMarkdownConverter(
    output_base_dir="output_docx_to_md",
    optimize_images=True,
    image_quality=85
)

# 转换单个文件
success, output_path, stats = converter.convert("input.docx")

if success:
    print(f"转换成功！输出: {output_path}")
    print(f"图片数: {stats['total_images']}")
    print(f"处理时间: {stats['processing_time']}秒")
else:
    print(f"转换失败: {stats.get('error')}")
```

## 转换效果示例

### 输入DOCX

包含数学公式、几何图形和文本的试卷。

### 输出Markdown

```markdown
# 2025年江苏省南京市中考数学试卷

## 一、选择题

1．（2分）﹣2的绝对值是（　　）

A．	B．	C．﹣2	D．2

![image1.png](images/image1.png)

A．P	B．Q	C．R	D．S
```

### 目录结构

```
output_docx_to_md/2025年江苏省南京市中考数学试卷/
├── document.md              # Markdown文本 (7KB)
├── images/                  # 图片目录
│   ├── image1.png          # 压缩后的图片
│   ├── image2.png
│   └── ...
└── meta.json               # 元数据
```

## 转换统计

### 实际测试数据（12个中考数学试卷）

| 指标 | 数据 |
|------|------|
| 总文件数 | 12 |
| 总图片数 | 579 |
| 平均每文件图片数 | 48 |
| 平均处理时间 | 1-2秒/文件 |
| 图片压缩率 | 73%-78% |
| 转换成功率 | 100% |

### 单文件示例

```
文件: 2025年江苏省南京市中考数学试卷.docx
大小: 544KB
图片: 30张
处理时间: 1.86秒

图片压缩统计:
- 原始大小: 557,386 bytes (0.53 MB)
- 压缩后: 132,559 bytes (0.13 MB)
- 节省空间: 424,827 bytes (76.2%)
```

## 工作原理

### 转换流程

```
DOCX输入
    ↓
1. LibreOffice转HTML (尝试提取图片)
    ↓ (失败)
2. python-docx直接提取图片
    ↓
3. 读取DOCX内容并提取OMML公式
    ↓
4. OMML公式转LaTeX
    ↓ (失败则保留为图片)
5. 生成Markdown文件
    ↓
6. 使用pngquant压缩图片
    ↓
7. 生成元数据JSON
    ↓
输出: Markdown + images/
```

### 图片提取策略

1. **优先使用LibreOffice**: 尝试将DOCX转为HTML，从HTML中提取图片
2. **降级到python-docx**: 如果LibreOffice未提取到图片，使用python-docx直接提取
3. **命名规则**: 图片按顺序命名为 `image1.png`, `image2.png`, ...

### 公式处理策略

1. **提取OMML**: 从DOCX中提取Office Math Markup Language (OMML)格式的公式
2. **转换为LaTeX**: 使用自定义转换器将OMML转为LaTeX
3. **降级处理**: 如果转换失败，将公式保留为图片

### 图片压缩策略

1. **工具**: 使用pngquant有损压缩
2. **质量**: 默认85 (范围1-100)
3. **格式**: 保持原格式（PNG/JPG等）
4. **效果**: 通常节省70%-80%空间

## 输出文件说明

### document.md

转换后的Markdown文件，包含：
- 文本内容
- 图片引用（相对路径）
- LaTeX公式（如果转换成功）

### meta.json

元数据文件，包含：

```json
{
  "input_file": "/path/to/input.docx",
  "output_dir": "/path/to/output",
  "total_images": 30,
  "extracted_images": 30,
  "total_formulas": 0,
  "converted_formulas": 0,
  "fallback_images": 0,
  "processing_time": 1.86,
  "success": true,
  "omml_conversion": {
    "total": 0,
    "success": 0,
    "failed": 0
  }
}
```

### conversion_log.md

批量转换日志，包含：
- 转换时间
- 转换统计表格
- 每个文件的详细结果

## 常见问题

### 1. LibreOffice转换失败

**现象**: 提示"LibreOffice转换失败"

**解决**:
- 脚本会自动降级到python-docx提取图片
- 确保 LibreOffice 已正确安装: `libreoffice --version`

### 2. 图片未提取

**现象**: 转换成功但images目录为空

**可能原因**:
- DOCX文件本身不包含图片（公式可能是文本格式）
- 图片嵌入方式特殊

**解决**:
- 检查原始DOCX文件
- 手动解压DOCX（ZIP格式）查看media目录

### 3. 公式显示为图片

**现象**: 数学公式不是LaTeX代码，而是图片引用

**原因**:
- DOCX中的公式可能本身就是图片格式，而非OMML格式
- OMML转LaTeX失败，降级为图片

**这是正常行为**: 许多试卷的公式就是以图片形式存储的

### 4. 图片压缩过度

**现象**: 压缩后图片质量太差

**解决**:
```bash
# 提高图片质量
python3 convert_docx_to_markdown.py input.docx --quality 95

# 或禁用压缩
python3 convert_docx_to_markdown.py input.docx --no-optimize
```

### 5. 处理速度慢

**可能原因**:
- 文件包含大量图片
- 系统I/O性能
- LibreOffice启动慢

**优化**:
- 批量处理时避免同时运行其他任务
- 使用SSD存储
- 可以修改脚本支持并行处理

## 性能优化建议

### 大批量处理

1. **并行处理**: 修改批量脚本支持多进程
2. **禁用压缩**: 如果不需要压缩，使用`--no-optimize`
3. **SSD存储**: 输入输出放在SSD上

### 图片质量优化

- **高质量需求**: `--quality 90-95`
- **标准质量**: `--quality 85` (默认)
- **高压缩率**: `--quality 70-80`

### 内存优化

处理超大DOCX文件时：
- 增加系统交换空间
- 分批处理文件
- 定期清理临时文件

## 故障排查

### 检查依赖

```bash
# 检查Python版本
python3 --version

# 检查Python依赖
pip3 list | grep -E "python-docx|latex2mathml"

# 检查LibreOffice
libreoffice --version

# 检查pngquant
which pngquant
```

### 测试转换

```bash
# 转换单个文件测试
python3 scripts/convert_docx_to_markdown.py test.docx

# 检查输出
ls -la output_docx_to_md/test/
```

### 查看日志

```bash
# 查看详细日志
python3 scripts/convert_docx_to_markdown.py test.docx 2>&1 | tee convert.log

# 查看批量转换日志
cat output_docx_to_md/conversion_log.md
```

## 高级用法

### 自定义OMML转换器

```python
from utils.omml_converter import OMMLConverter

converter = OMMLConverter()
success, latex = converter.omml_to_latex(omml_xml)
```

### 自定义图片优化

```python
from utils.image_optimizer import ImageOptimizer

optimizer = ImageOptimizer(quality=90)
success, orig_size, opt_size = optimizer.optimize_image("image.png")
```

### 集成到其他项目

```python
import sys
sys.path.insert(0, 'scripts')

from convert_docx_to_markdown import DocxToMarkdownConverter

converter = DocxToMarkdownConverter()
success, output, stats = converter.convert("document.docx")
```

## 贡献指南

### 改进建议

1. **并行处理**: 支持多进程批量转换
2. **更多格式**: 支持DOC、RTF等格式
3. **OCR集成**: 对公式图片进行OCR识别
4. **表格优化**: 改进复杂表格的转换
5. **样式保留**: 保留更多格式样式

### 提交代码

1. Fork项目
2. 创建功能分支
3. 提交Pull Request

## 许可证

本项目是Assistant Expert Tools的子项目，遵循相同的许可证。

## 更新日志

### v1.0.0 (2026-02-15)

- ✅ 初始版本发布
- ✅ 支持DOCX转Markdown
- ✅ 支持图片提取和压缩
- ✅ 支持OMML公式转LaTeX
- ✅ 批量处理功能
- ✅ 详细的转换日志

## 联系方式

- 项目维护者: Claude Code Subproject Team
- 问题反馈: GitHub Issues
- 技术讨论: GitHub Discussions

---

**最后更新**: 2026-02-15
**文档版本**: 1.0.0
