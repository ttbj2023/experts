# 核心转换脚本对比分析

生成时间：2026-02-17

## 📋 概览

| 脚本 | 功能 | 代码量 | 架构阶段 | 主要模型 |
|------|------|--------|----------|----------|
| `convert_pdf_complete.py` | PDF → Markdown | 1073行 | 5阶段 | GLM-4.6V + OpenCV + DeepSeek |
| `convert_docx_to_markdown_v3.py` | DOCX → Markdown | 1224行 | 4阶段 | LibreOffice + GLM-4.6V + DeepSeek |

---

## 1. convert_pdf_complete.py 详细分析

### 🎯 定位
**专业PDF处理工具** - 适用于原始PDF文档（非从DOCX转换）

### 🏗️ 完整架构（5阶段）

#### Stage 1: GLM-4.6V-Flash OCR + 图片占位符
```python
# 核心逻辑
def stage1_ocr_with_placeholders(pdf_path, max_pages, dpi=200):
    # 1. 使用PyMuPDF渲染PDF页面
    page = pdf[page_num]
    pix = page.get_pixmap(matrix=mat)
    
    # 2. 调用GLM-4.6V-Flash进行OCR
    response = glm_processor.call_glm46v_api(image_base64, prompt)
    
    # 3. 生成占位符格式: ![desc](IMAGE_PLACEHOLDER)
    raw_markdown = response['choices'][0]['message']['content']
```

**特点**：
- 使用本地GLM-4.6V-Flash服务（http://192.168.100.110:9999）
- 生成Markdown格式的占位符
- 支持页眉页脚过滤

#### Stage 1.5: DeepSeek排版优化（可选）
```python
def format_markdown_with_deepseek(markdown):
    prompt = """你是一个专业的Markdown排版专家。
    ## 排版要求
    ### 1. 标题层级规范
    - 一级标题：# 一、茶树的起源
    - 二级标题：## (一) 茶树起源的佐证
    ...
    """
```

**优势**：
- 智能优化标题层级
- 规范列表格式
- 移除页面断句和页码
- 修复OCR错误

#### Stage 2: OpenCV精确图片提取
```python
def _detect_images_with_opencv(page_image, page_num):
    # 1. Canny边缘检测
    edges = cv2.Canny(gray, 50, 150)
    
    # 2. 膨胀边缘
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # 3. 查找轮廓
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. 合并重叠的bbox
    images_info = _merge_overlapping_bboxes(images_info)
```

**优势**：
- 自动检测图片区域
- 不依赖PDF元数据
- 可检测嵌入式图片

**劣势**：
- 可能漏掉某些图片
- 需要调参（min_area等）

#### Stage 3: GLM-4V图片描述
```python
def _describe_single_image(image_path, max_size=1920):
    # 1. 压缩图片到1920px
    img.thumbnail((max_size, max_size))
    
    # 2. 转换为JPEG
    img.save(buffer, format='JPEG', quality=85)
    
    # 3. 调用GLM-4V API
    payload = {
        "model": "zai-org/glm-4.6v-flash",
        "messages": [{"role": "user", "content": [...]_]
    }
```

**特点**：
- 生成详细的图片描述
- 识别文字、标注、数据
- 压缩图片以节省带宽

#### Stage 4: DeepSeek语义匹配
```python
def stage4_match_placeholders(markdown, placeholders, image_descriptions):
    # 传递完整文档上下文
    prompt = f"""
    ## 完整Markdown文档
    {markdown[:30000]}
    
    ## 占位符列表
    ...
    
    ## 图片描述列表
    ...
    """
```

**特点**：
- 分析完整文档上下文
- 理解每个占位符的语义
- 返回JSON格式的匹配映射

#### Stage 5: 替换占位符
```python
def stage5_replace_placeholders(markdown, placeholders, mapping, images_dir):
    # 按索引倒序替换（避免位置偏移）
    sorted_placeholders = sorted(placeholders, key=lambda x: x['index'], reverse=True)
    
    for placeholder in sorted_placeholders:
        if idx in mapping:
            image_path = os.path.join('extracted_images', image_filename)
            markdown = markdown.replace(full_match, f'![{type}]({image_path})')
```

**特点**：
- 倒序替换避免位置偏移
- 未匹配的占位符直接删除

### 🔑 核心优势

1. **完整的流水线设计** - 5个阶段清晰分离
2. **OpenCV自动检测** - 不依赖PDF元数据
3. **可选的排版优化** - DeepSeek智能格式化
4. **页眉页脚清理** - 自动移除重复内容
5. **适合复杂PDF** - 扫描版、图片版等

### ⚠️ 主要劣势

1. **图片质量受限** - 依赖PDF渲染质量
2. **OpenCV可能漏检** - 需要调参
3. **没有文档分段** - 超长文档可能失败
4. **缺少重复检测** - 可能出现重复匹配

---

## 2. convert_docx_to_markdown_v3.py 详细分析

### 🎯 定位
**专业DOCX处理工具** - 保留原始图片质量，适合科技文档

### 🏗️ 完整架构（4阶段）

#### Stage 1: 三步识别流程
```python
def _stage1_pdf_recognition(docx_path, pdf_path, md_path, images_dir):
    # 步骤1.1: 从DOCX提取原始图片
    docx_images, _ = self._extract_images_from_docx(docx_path, images_dir)
    
    # 步骤1.2: DOCX → PDF (LibreOffice)
    pdf_success = self._convert_docx_to_pdf(docx_path, pdf_path)
    
    # 步骤1.3: PDF → Markdown (GLM-4.6V-Flash)
    markdown_content = self._convert_pdf_with_glm46v(pdf_path, md_path)
```

**关键特点**：
- **提取原始图片**：使用python-docx直接从DOCX提取，保留原始质量
- **LibreOffice转换**：DOCX → PDF，确保格式兼容
- **生成HTML注释占位符**：`<!-- IMAGE_PLACEHOLDER type: xxx description: xxx -->`

#### Stage 2: GLM-4.6V-Flash图片描述
```python
def _stage2_describe_images(docx_images, images_dir):
    for idx, img_info in enumerate(docx_images, 1):
        description = self._describe_single_image(image_path)
        image_descriptions.append({
            'filename': filename,
            'description': description
        })
```

**特点**：
- 串行处理每张图片
- 生成详细描述
- 清理GLM的think标签

#### Stage 3: DeepSeek全局语义匹配
```python
def _stage3_semantic_matching(md_path, image_descriptions):
    # 1. 读取整个md文档（作为上下文）
    md_content = f.read()
    
    # 2. 提取占位符
    placeholders = self._extract_placeholders(md_path)
    
    # 3. 如果文档>64k字符，自动分段
    doc_parts = self._split_document_by_placeholders(md_content, placeholders, 64000)
```

**核心优势**：
- **全局上下文理解**：分析完整文档
- **智能文档分段**：支持超长文档（>64k字符）
- **分段匹配策略**：每个部分独立匹配后合并

#### Stage 4: 智能占位符替换
```python
def _stage4_replace_placeholders(md_path, mapping, images_dir, image_descriptions):
    # 1. 移除无效的代码块（GLM误识别的```标记）
    content = self._remove_invalid_code_blocks(content)
    
    # 2. 移除PDF页面分隔符（孤立的---）
    content = self._remove_pdf_page_separators(content)
    
    # 3. 检测并处理重复匹配
    duplicate_images = {img: indices for img, indices in image_usage.items() if len(indices) > 1}
```

**核心特性**：

##### 3.1 无效代码块清理
```python
def _remove_invalid_code_blocks(content):
    """
    移除GLM-4.6V-Flash误识别的无效代码块
    策略：DOCX文档不应该有代码块，移除所有```标记
    """
    # 检测代码块开始标记
    if line.strip().startswith('```'):
        # 提取代码块内容并保留（移除```标记）
        # 去除每行的缩进
```

##### 3.2 PDF页面分隔符清理
```python
def _remove_pdf_page_separators(content):
    """
    移除GLM-4.6V-Flash添加的PDF页面分隔符
    策略：只移除"孤立的"页面分隔符
    """
    # 检查是否是孤立的页面分隔符
    # 特征：前后都是空行，或者是文档边界
    prev_is_empty = (i == 0) or (prev_line == '')
    next_is_empty = (i == len(lines) - 1) or (next_line == '')
```

##### 3.3 重复匹配检测
```python
# 统计每个图片被匹配的次数
for placeholder_idx, image_filename in mapping.items():
    if image_filename not in image_usage:
        image_usage[image_filename] = []
    image_usage[image_filename].append(placeholder_idx)

# 找出被多次使用的图片
duplicate_images = {img: indices for img, indices in image_usage.items() if len(indices) > 1}

# 只在最后一个位置插入图片
last_index = max(indices)
for idx in indices:
    if idx != last_index:
        del mapping[idx]  # 移除前面位置的匹配
```

### 🔑 核心优势

1. **保留原始图片质量** - 直接从DOCX提取，不依赖PDF渲染
2. **智能文档分段** - 支持超长文档（>64k字符）
3. **重复匹配检测** - 自动处理同一图片匹配到多个占位符
4. **无效代码块清理** - 移除GLM误识别的```标记
5. **页面分隔符清理** - 智能识别孤立的---
6. **HTML注释占位符** - 更灵活，可携带更多元数据

### ⚠️ 主要劣势

1. **依赖LibreOffice** - 需要外部软件
2. **没有排版优化** - 缺少DeepSeek格式化
3. **没有页眉页脚清理** - 依赖GLM识别
4. **串行处理** - Stage 2没有并发，性能受限

---

## 3. 两个脚本的深度对比

### 📊 功能对比表

| 功能维度 | convert_pdf_complete.py | convert_docx_to_markdown_v3.py | 胜出 |
|---------|------------------------|------------------------------|------|
| **输入格式** | PDF | DOCX | - |
| **图片提取策略** | OpenCV检测（计算机视觉） | DOCX直接提取（文档解析） | v3（质量）|
| **图片质量** | PDF渲染质量 | 原始图片质量 | **v3** |
| **OCR模型** | GLM-4.6V-Flash | GLM-4.6V-Flash | 平手 |
| **排版优化** | ✅ DeepSeek（可选） | ❌ 无 | **complete** |
| **页眉页脚清理** | ✅ 主动清理 | ❌ 依赖GLM | **complete** |
| **代码块清理** | ❌ 无 | ✅ 有 | **v3** |
| **页面分隔符清理** | ❌ 无 | ✅ 有 | **v3** |
| **重复匹配检测** | ❌ 无 | ✅ 有 | **v3** |
| **文档分段** | ❌ 无 | ✅ 有（64k阈值） | **v3** |
| **占位符格式** | Markdown: `![desc](IMAGE_PLACEHOLDER)` | HTML注释: `<!-- ... -->` | **v3**（更灵活）|
| **最终格式** | `![type](path)` | `![图片：desc](path)` | **v3**（更详细）|
| **外部依赖** | OpenCV | LibreOffice | complete（更轻量）|
| **并发处理** | ❌ 无 | ❌ 无 | 平手 |
| **缓存机制** | ❌ 无 | ❌ 无 | 平手 |

### 🎯 适用场景推荐

#### 选择 `convert_pdf_complete.py` 当：

✅ **输入是原始PDF**（非从DOCX转换）
```bash
# 示例：处理扫描版数学教材
python scripts/convert_pdf_complete.py \
  "scanned_math_textbook.pdf" \
  -o output/ \
  --format-with-deepseek
```

✅ **PDF是扫描版或图片版**
- OpenCV可以自动检测图片区域
- GLM-4.6V-Flash进行OCR识别

✅ **需要排版优化**
- 使用`--format-with-deepseek`启用
- 智能优化标题层级和列表格式

✅ **需要自动页眉页脚清理**
- 内置页眉页脚模式识别
- 自动移除重复内容

#### 选择 `convert_docx_to_markdown_v3.py` 当：

✅ **输入是DOCX原始文档**
```bash
# 示例：处理Word版数学试卷
python scripts/convert_docx_to_markdown_v3.py \
  "math_exam.docx" \
  -o output/ \
  --glm-api http://192.168.100.110:9999
```

✅ **需要保留原始图片质量**
- 直接从DOCX提取原始图片
- 不依赖PDF渲染质量

✅ **文档包含GLM误识别的代码块**
- 自动移除```标记
- 保留代码块内的ASCII art等

✅ **文档包含PDF页面分隔符**
- 智能识别孤立的---
- 保留有实际用途的分隔符

✅ **可能出现重复图片匹配**
- 自动检测并处理
- 只保留最后一个位置

✅ **文档很长（>64k字符）**
- 自动分段处理
- 支持超长文档

### 💡 架构设计对比

#### 完整性
- **complete.py**: 5阶段，更完整
- **v3.py**: 4阶段，更聚焦

#### 模块化
- **complete.py**: 按stage分离，清晰
- **v3.py**: 私有方法分离，优秀

#### 可扩展性
- **complete.py**: 易于添加新stage
- **v3.py**: 易于添加新后处理

#### 错误处理
- **complete.py**: 完善
- **v3.py**: 更完善（更多try-catch）

### 🔧 代码质量对比

| 指标 | convert_pdf_complete.py | convert_docx_to_markdown_v3.py |
|------|------------------------|------------------------------|
| **代码行数** | 1073行 | 1224行 |
| **注释率** | 中等（主要在docstring） | 高（详细的中文注释） |
| **类型注解** | 部分有 | 部分有 |
| **文档字符串** | 完善 | 非常完善 |
| **日志输出** | 详细 | 非常详细 |
| **模块化程度** | 好 | 优秀 |
| **错误处理** | 完善 | 更完善 |

---

## 4. 代码复用分析

### 🔍 重复代码识别

#### 1. GLM-4.6V-Flash API调用（重复度：90%）
```python
# convert_pdf_complete.py (line 533-602)
def _describe_single_image(self, image_path: str, max_size: int = 1920):
    img = Image.open(image_path)
    img.thumbnail((max_size, max_size))
    # ... 转换为JPEG，调用API
    response = requests.post(f"{self.glm_api_url}/v1/chat/completions", ...)

# convert_docx_to_markdown_v3.py (line 667-745)
def _describe_single_image(self, image_path: str, max_size: int = 1280):
    img = Image.open(image_path)
    img.thumbnail((max_size, max_size))
    # ... 转换为JPEG，调用API
    response = requests.post(f"{self.glm_api_url}/v1/chat/completions", ...)
```

#### 2. DeepSeek语义匹配（重复度：60%）
```python
# convert_pdf_complete.py (line 604-753)
def stage4_match_placeholders(markdown, placeholders, image_descriptions):
    prompt = f"...完整文档{markdown[:30000]}..."
    # 调用DeepSeek API

# convert_docx_to_markdown_v3.py (line 973-1188)
def _call_deepseek_for_matching_global(md_content, placeholders, image_descriptions):
    # 支持文档分段（64k阈值）
    doc_parts = self._split_document_by_placeholders(...)
    # 调用DeepSeek API
```

#### 3. 占位符提取（重复度：40%）
- 两个脚本都有提取占位符的逻辑
- 只是占位符格式不同

### 🛠️ 重构建议

#### 方案1：提取公共模块
```
scripts/
├── core/
│   ├── __init__.py
│   ├── glm_client.py          # GLM-4.6V-Flash客户端
│   ├── deepseek_client.py     # DeepSeek客户端
│   ├── image_processor.py     # 图片处理工具
│   └── placeholder.py         # 占位符处理
├── convert_pdf_complete.py    # 重构后使用core模块
└── convert_docx_to_markdown_v3.py  # 重构后使用core模块
```

#### 方案2：统一占位符格式
建议统一使用HTML注释格式：
```html
<!-- IMAGE_PLACEHOLDER
  type: 几何图形
  description: 直角三角形ABC示意图
  page: 5
-->
```

**优势**：
- 更容易解析
- 可携带更多元数据
- 不干扰Markdown渲染

#### 方案3：提取图片处理工具类
```python
# core/image_processor.py
class ImageProcessor:
    @staticmethod
    def compress_for_glm(image_path: str, max_size: int = 1280) -> str:
        """压缩图片并转换为base64（用于GLM）"""
        pass

    @staticmethod
    def extract_from_docx(docx_path: str, output_dir: str) -> List[Dict]:
        """从DOCX提取图片"""
        pass

    @staticmethod
    def detect_with_opencv(page_image: str) -> List[Dict]:
        """使用OpenCV检测图片"""
        pass
```

### 📊 重构效果预估

| 指标 | 重构前 | 重构后 | 改善 |
|------|--------|--------|------|
| **代码重复率** | ~30% | <10% | **67%↓** |
| **总代码量** | 2297行 | ~2800行 | +21% |
| **可维护性** | 中 | 高 | **↑↑** |
| **可测试性** | 中 | 高 | **↑↑** |
| **扩展性** | 低 | 高 | **↑↑↑** |

---

## 5. 性能优化建议

### 🚀 优化1：并发处理图片描述

**当前问题**：
- 两个脚本都是串行处理图片
- Stage 2描述30张图片需要~1-2分钟

**优化方案**：
```python
from concurrent.futures import ThreadPoolExecutor

def _stage2_describe_images_concurrent(self, docx_images, images_dir, max_workers=5):
    """并发描述图片"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(self._describe_single_image, img['path']): img
            for img in docx_images
        }
        
        for future in futures:
            description = future.result()
            # ...
```

**效果**：
- 5线程并发：~15-25秒（原来1-2分钟）
- **提速70-80%**

### 💾 优化2：添加缓存机制

**当前问题**：
- 每次运行都重新调用GLM和DeepSeek
- 没有缓存中间结果

**优化方案**：
```python
import hashlib
from pathlib import Path

class CachedGLMClient:
    def describe_image(self, image_path: str) -> str:
        """带缓存的图片描述"""
        # 生成缓存键
        img_hash = hashlib.md5(Path(image_path).read_bytes()).hexdigest()
        cache_file = self.cache_dir / f"desc_{img_hash}.json"

        # 检查缓存
        if cache_file.exists():
            return json.loads(cache_file.read_text())['description']

        # 调用API并缓存
        description = self._call_glm_api(image_path)
        cache_file.write_text(json.dumps({'description': description}))
        return description
```

**效果**：
- 重复运行相同文档：**接近0秒**（直接读缓存）
- 磁盘空间：每张图片~1KB缓存

### 📦 优化3：批量处理优化

**当前问题**：
- 每个文档单独处理
- 没有批量处理优化

**优化方案**：
```python
def batch_convert(input_files: List[str], output_dir: str, max_workers: int = 3):
    """批量转换多个文档"""
    # 先提取所有图片（可以并发）
    # 然后并发处理OCR
    # 最后并发进行语义匹配
    pass
```

---

## 6. 总结与建议

### ✅ 核心优势总结

#### convert_pdf_complete.py
- ✅ 完整的5阶段流水线设计
- ✅ OpenCV自动检测图片区域
- ✅ DeepSeek排版优化（可选）
- ✅ 页眉页脚自动清理
- ✅ 适合复杂PDF文档
- ✅ 外部依赖较轻（只需OpenCV）

#### convert_docx_to_markdown_v3.py
- ✅ 保留原始图片质量
- ✅ 智能文档分段（64k阈值）
- ✅ 重复匹配检测
- ✅ 无效代码块清理
- ✅ 页面分隔符清理
- ✅ 更完善的错误处理
- ✅ HTML注释占位符（更灵活）

### ⚠️ 共同问题

1. **代码重复** - ~30%重复代码，急需重构
2. **缺少测试** - 没有单元测试和集成测试
3. **配置管理** - 没有配置文件，依赖命令行参数
4. **性能监控** - 缺少详细的性能统计和监控
5. **缓存机制** - 没有缓存，重复运行浪费资源
6. **串行处理** - Stage 2没有并发，性能受限

### 🎯 推荐行动计划

#### 短期（1-2周）
1. ✅ 提取公共模块到`core/`目录
2. ✅ 统一GLM和DeepSeek客户端
3. ✅ 添加基础单元测试
4. ✅ 统一占位符格式

#### 中期（1个月）
1. ✅ 实现并发处理（ThreadPoolExecutor）
2. ✅ 添加缓存机制
3. ✅ 完善文档和使用示例
4. ✅ 添加性能监控和统计

#### 长期（2-3个月）
1. ✅ 开发Web界面
2. ✅ 支持更多输入格式（EPUB、HTML等）
3. ✅ 集成更多模型（GPT-4V、Claude等）
4. ✅ 性能分析和优化
5. ✅ 插件化架构

---

**报告生成者**: Claude Code
**日期**: 2026-02-17
**文档版本**: 1.0.0
