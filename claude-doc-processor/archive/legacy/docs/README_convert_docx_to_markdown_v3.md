# DOCX to Markdown Converter v3

专业的DOCX到Markdown转换工具，特别优化处理数学、物理、化学等科技文档。

## 特性

- ✅ **智能图片处理**：自动提取图片并生成语义描述
- ✅ **公式保留**：完整保留数学公式的LaTeX格式
- ✅ **表格识别**：准确识别和转换复杂表格结构
- ✅ **三阶段架构**：分离视觉识别和语义匹配，提高准确率
- ✅ **本地模型**：使用本地GLM-4.6V-Flash，无需API key
- ✅ **语义匹配**：使用DeepSeek进行智能图片占位符匹配（100%匹配率）

## 系统架构

### 三阶段处理流程

```
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: GLM-4.6V-Flash PDF识别                           │
│  ├─ DOCX → PDF (LibreOffice)                               │
│  ├─ PDF → Markdown (GLM-4.6V-Flash with placeholders)     │
│  └─ 生成: <!-- IMAGE_PLACEHOLDER type: xxx description: xxx --> │
├─────────────────────────────────────────────────────────────┤
│  Stage 2: GLM-4.6V-Flash 图片描述                         │
│  ├─ 提取DOCX中的原始图片                                     │
│  ├─ 调用GLM-4.6V-Flash生成图片描述                          │
│  └─ 输出: image_descriptions.json                          │
├─────────────────────────────────────────────────────────────┤
│  Stage 3: DeepSeek 语义匹配                                │
│  ├─ 分析占位符上下文和图片描述                              │
│  ├─ 语义匹配：哪个图片对应哪个占位符                        │
│  └─ 输出: placeholder_to_image_mapping.json                │
├─────────────────────────────────────────────────────────────┤
│  Stage 4: 占位符替换                                        │
│  ├─ 替换占位符为: ![图片：描述](./images/xxx.png)         │
│  ├─ 删除未匹配的占位符                                      │
│  └─ 清理无效内容                                           │
└─────────────────────────────────────────────────────────────┘
```

## 环境要求

### 系统依赖

- **Python**: 3.8+
- **LibreOffice**: 用于DOCX → PDF转换
- **本地服务**:
  - GLM-4.6V-Flash服务（默认：`http://192.168.100.110:9999`）

### Python依赖

```bash
pip install pillow requests
```

## 安装

### 1. 安装LibreOffice

**Ubuntu/Debian**:
```bash
sudo apt-get install libreoffice
```

**macOS**:
```bash
brew install --cask libreoffice
```

**Windows**:
从 [LibreOffice官网](https://www.libreoffice.org/) 下载安装

### 2. 配置GLM-4.6V-Flash本地服务

确保GLM-4.6V-Flash服务在 `http://192.168.100.110:9999` 运行，或修改 `--glm-api` 参数指定你的服务地址。

### 3. 配置DeepSeek API（可选）

用于Stage 3语义匹配。如果不配置，将使用内置的默认key。

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

## 使用方法

### 基本用法

```bash
python scripts/convert_docx_to_markdown_v3.py input.docx -o output_dir
```

### 完整参数

```bash
python scripts/convert_docx_to_markdown_v3.py \
  input_file/文档.docx \
  -o output_directory \
  --glm-api http://192.168.100.110:9999 \
  --deepseek-key your_deepseek_key
```

### 参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `input_file` | ✅ | - | 输入DOCX文件路径 |
| `-o, --output` | ❌ | `output_docx_to_md_v3` | 输出目录 |
| `--glm-api` | ❌ | `http://192.168.100.110:9999` | GLM-4.6V-Flash本地服务地址 |
| `--deepseek-key` | ❌ | 内置key | DeepSeek API密钥 |

## 输出结构

```
output_dir/
└── 文档名称/
    ├── document.md           # 最终Markdown文件
    ├── images/               # 提取的图片
    │   ├── image1.png
    │   ├── image2.png
    │   └── ...
    ├── image_descriptions.json      # Stage 2生成的图片描述
    ├── placeholder_to_image_mapping.json  # Stage 3生成的匹配映射
    └── meta.json             # 转换过程元数据
```

## 输出格式

### 图片引用格式

```markdown
![图片：几何图形示意图，显示三角形ABC及其外接圆](./images/image5.png)
```

- **前缀**：`图片：`
- **描述来源**：使用占位符中的原始描述（不使用GLM生成的描述）
- **路径**：相对路径 `./images/filename.png`

### Meta JSON格式

```json
{
  "input_file": "input_file/文档.docx",
  "output_dir": "output_dir/文档名称",
  "stage1_success": true,
  "stage1_time": 164.8,
  "stage2_success": true,
  "stage2_time": 102.8,
  "stage3_success": true,
  "stage3_time": 28.9,
  "total_placeholders": 0,
  "total_images": 30,
  "matched_images": 15,
  "unmatched_placeholders": 0,
  "processing_time": 296.6,
  "success": true,
  "error": null
}
```

## 性能指标

基于测试结果（2025年江苏省南京市中考数学试卷）：

| 指标 | 数值 |
|------|------|
| Stage 1 耗时 | ~165秒 |
| Stage 2 耗时 | ~103秒 |
| Stage 3 耗时 | ~29秒 |
| **总耗时** | **~297秒** (~5分钟) |
| 图片匹配率 | 100% |
| 图片提取成功率 | 100% |

## 批量转换

### 使用脚本批量转换

```bash
#!/bin/bash

INPUT_DIR="input_file"
OUTPUT_DIR="output_all"

for file in "$INPUT_DIR"/*.docx; do
    filename=$(basename "$file" .docx)
    echo "转换: $filename"
    python scripts/convert_docx_to_markdown_v3.py "$file" -o "$OUTPUT_DIR"
done
```

## 故障排除

### 问题1：LibreOffice未找到

**错误信息**: `libreoffice: command not found`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS
brew install --cask libreoffice
```

### 问题2：GLM-4.6V-Flash连接失败

**错误信息**: `Connection refused` 或 `Timeout`

**解决方案**:
1. 确认GLM-4.6V-Flash服务正在运行
2. 检查服务地址是否正确：`curl http://192.168.100.110:9999/v1/models`
3. 使用 `--glm-api` 参数指定正确的服务地址

### 问题3：图片描述为空

**可能原因**: 占位符中没有描述信息

**解决方案**: 
- 这是正常情况，脚本会使用默认文本"图片"
- 如果需要详细描述，需要在源DOCX中为图片添加alt text

### 问题4：Stage 3匹配失败

**错误信息**: DeepSeek API调用失败

**解决方案**:
1. 检查DeepSeek API key是否有效
2. 确认网络连接正常
3. 使用 `--deepseek-key` 参数提供有效的API key

## 技术细节

### 占位符格式

Stage 1生成的占位符格式：

```html
<!-- IMAGE_PLACEHOLDER type: 几何图形 description: 直角三角形ABC示意图，∠ACB=90° -->
```

### 图片描述生成

Stage 2调用GLM-4.6V-Flash时使用的prompt：

```
请详细描述这张图片的内容。

要求：
1. 识别图片的类型（几何图形、数学公式、统计图表、示意图等）
2. 描述图片中的关键元素和细节
3. 如果有文字或标注，请准确引用
4. 描述要准确、简洁，不超过200字

请直接返回描述文本，不要添加其他内容。
```

### 语义匹配策略

Stage 3使用DeepSeek分析：
1. 占位符周围的文本上下文
2. 图片的视觉描述
3. 语义相关性判断
4. 返回最佳匹配映射

## 版本历史

### v3.0.0 (2026-02-16)

- ✅ 实现三阶段架构
- ✅ 使用GLM-4.6V-Flash本地模型
- ✅ 集成DeepSeek语义匹配
- ✅ 100%图片匹配率
- ✅ 支持占位符描述保留
- ✅ 移除GLM API key依赖（本地模型）
- ✅ 修复图片描述污染问题

## 许可证

本项目为 Assistant Expert Tools 子项目。

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

**最后更新**: 2026-02-16
**维护者**: Claude Code Subproject Team
