#!/usr/bin/env python3
"""
PDF转Markdown（完整版）- 整合所有组件
1. GLM-4.6V-Flash: OCR + 图片占位符
2. OpenCV: 精确图片提取
3. GLM-4V: 图片描述生成
4. DeepSeek: 语义匹配
5. 占位符替换
"""

import os
import sys
import json
import re
import io
import base64
import requests
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image
import logging

# 导入GLM处理器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from process_pdf_with_glm46v_universal import GLM46VProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompletePDFConverter:
    """完整的PDF转换器 - 整合所有组件"""

    def __init__(
        self,
        glm_api_url: str = 'http://192.168.100.110:9999',
        glm_api_key: str = None,
        deepseek_api_key: str = None,
        format_with_deepseek: bool = False
    ):
        """
        初始化转换器

        Args:
            glm_api_url: GLM API地址
            glm_api_key: GLM API密钥（可选）
            deepseek_api_key: DeepSeek API密钥
            format_with_deepseek: 是否使用DeepSeek进行排版优化
        """
        self.glm_api_url = glm_api_url
        self.glm_api_key = glm_api_key or os.getenv('GLM_API_KEY', '')
        self.deepseek_api_key = deepseek_api_key or os.getenv('DEEPSEEK_API_KEY', 'sk-62f31b03e22048799beefff7cae0dfc3')
        self.format_with_deepseek = format_with_deepseek

        # 初始化GLM处理器
        self.glm_processor = GLM46VProcessor(api_url=glm_api_url)

        logger.info("初始化完整PDF转换器")
        logger.info(f"  GLM API: {glm_api_url}")
        logger.info(f"  DeepSeek: {'已配置' if self.deepseek_api_key else '未配置'}")
        logger.info(f"  排版优化: {'启用' if format_with_deepseek else '禁用'}")

    def clean_think_tags(self, text: str) -> str:
        """移除GLM的思考过程标签 </think>...
"""
        pattern = r'​*​*​*'
        cleaned = re.sub(pattern, '', text, flags=re.DOTALL)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    def extract_markdown_content(self, text: str) -> str:
        """智能提取真正的Markdown内容"""
        text = self.clean_think_tags(text)

        # 查找 ```markdown 代码块
        markdown_block_pattern = r'```markdown\s*\n(.*?)\n```'
        matches = re.findall(markdown_block_pattern, text, re.DOTALL)
        if matches and len(matches[-1]) > 100:
            return matches[-1].strip()

        return text

    def clean_headers_footers(self, markdown: str) -> str:
        """
        后处理：清理常见的页眉页脚模式

        Args:
            markdown: Markdown文本

        Returns:
            清理后的Markdown
        """
        lines = markdown.split('\n')
        cleaned_lines = []

        # 定义页眉页脚模式
        header_footer_patterns = [
            r'^\s*[第0-9一二三四五六七八九十百千]+\s*页\s*$',  # "第1页", "第 1 页"
            r'^\s*-\s*\d+\s*-\s*$',  # "- 1 -"
            r'^\s*Page\s+\d+\s*$',  # "Page 1"
            r'^\s*\d+\s*/\s*\d+\s*$',  # "1/10"
            r'^\s*[第0-9一二三四五六七八九十百千]+[章节篇卷部册].*$',  # 重复的章节标题
            r'^\s*图书名称.*书名.*$',  # 书名
            r'^\s*_+\s*$',  # 分隔线
            r'^\s*-+\s*$',  # 分隔线
            r'^\s*={3,}\s*$',  # 分隔线（3个以上=号）
        ]

        # 第一遍：移除明显的页眉页脚
        for line in lines:
            is_header_or_footer = False

            for pattern in header_footer_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_header_or_footer = True
                    break

            # 检查是否是纯数字或短符号行（可能是页码）
            if not is_header_or_footer:
                stripped = line.strip()
                if len(stripped) <= 10 and (
                    stripped.isdigit() or
                    re.match(r'^[-=_]{3,}$', stripped)
                ):
                    is_header_or_footer = True

            if not is_header_or_footer:
                cleaned_lines.append(line)

        # 第二遍：移除文档开头和结尾的重复短行
        if len(cleaned_lines) > 10:
            # 移除开头的短行（可能是页眉）
            start_idx = 0
            for i in range(min(5, len(cleaned_lines))):
                if len(cleaned_lines[i].strip()) > 20:
                    start_idx = i
                    break

            # 移除结尾的短行（可能是页脚）
            end_idx = len(cleaned_lines)
            for i in range(len(cleaned_lines) - 1, max(0, len(cleaned_lines) - 5), -1):
                if len(cleaned_lines[i].strip()) > 20:
                    end_idx = i + 1
                    break

            cleaned_lines = cleaned_lines[start_idx:end_idx]

        # 重新组合
        cleaned = '\n'.join(cleaned_lines)

        # 清理多余的空行
        cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)

        return cleaned.strip()

    def format_markdown_with_deepseek(self, markdown: str) -> str:
        """
        使用DeepSeek-chat进行Markdown排版优化

        Args:
            markdown: 待优化的Markdown文本

        Returns:
            优化后的Markdown文本
        """
        if not self.deepseek_api_key:
            logger.warning("未配置DeepSeek API密钥，跳过排版优化")
            return markdown

        logger.info("\n" + "="*60)
        logger.info("Stage 1.5: DeepSeek排版优化")
        logger.info("="*60)
        logger.info(f"输入字符数: {len(markdown):,}")

        # 构建排版prompt
        prompt = f"""你是一个专业的Markdown排版专家。请对以下OCR识别的Markdown文本进行排版优化。

## 排版要求

### 1. 标题层级规范
- 一级标题：使用 `#` （如：# 一、茶树的起源）
- 二级标题：使用 `##` （如：## (一) 茶树起源的佐证）
- 三级标题：使用 `###` （如：### 1. 最早的茶字）
- 四级标题：使用 `####` （如：#### (1) "茶"字的由来）
- 五级标题：使用 `#####` （如：##### ① 若）

规则：
- 标题序号保留中文数字（一、二、三）和阿拉伯数字（1、2、3）
- 括号标题保留括号（（一）、(1)）
- 列表标记（①②③）前添加 `##### ` 作为五级标题

### 2. 列表格式规范
- 无序列表：使用 `- ` 开头（如：- 第一点）
- 有序列表：使用 `1. ` 开头（如：1. 第一步）
- 嵌套列表：使用缩进（2空格或4空格）

### 3. 页面连接处理
- 移除页面之间的断句（如孤立的句子片段）
- 保持段落的完整性
- 移除误识别的页码（如单独成行的数字）

### 4. 文本清理
- 移除多余空行（保留1个空行分隔段落）
- 移除行首行尾多余空格
- 修复明显的OCR错误

### 5. 格式统一
- 标题与内容之间保留1个空行
- 段落之间保留1个空行
- 列表项之间不保留空行

## 输入文本

```
{markdown}
```

## 输出要求

1. **只输出优化后的Markdown内容**，不要有解释或前言
2. 保持原意不变，只优化格式
3. 不要删除任何内容
4. 输出必须是纯Markdown格式，不要使用markdown代码块包裹

现在请开始排版优化：
"""

        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 8192,
                    "stream": False
                },
                timeout=300
            )

            response.raise_for_status()
            result = response.json()

            # 提取格式化后的内容
            formatted_text = result['choices'][0]['message']['content'].strip()

            # 移除可能的markdown代码块包裹
            if formatted_text.startswith('```markdown'):
                formatted_text = formatted_text[13:]
            if formatted_text.startswith('```'):
                formatted_text = formatted_text[3:]
            if formatted_text.endswith('```'):
                formatted_text = formatted_text[:-3]

            formatted_text = formatted_text.strip()

            logger.info(f"输出字符数: {len(formatted_text):,}")
            logger.info("✅ 排版优化完成")

            return formatted_text

        except Exception as e:
            logger.error(f"❌ 排版优化失败: {e}")
            logger.warning("将使用原始Markdown继续处理")
            return markdown


    # ============ Stage 1: OCR + 图片占位符 ============

    def stage1_ocr_with_placeholders(
        self,
        pdf_path: str,
        max_pages: int = None,
        dpi: int = 200
    ) -> Tuple[str, List[Dict]]:
        """
        Stage 1: 使用GLM-4.6V-Flash进行OCR并生成图片占位符

        Args:
            pdf_path: PDF文件路径
            max_pages: 最大处理页数
            dpi: 渲染DPI

        Returns:
            (markdown内容, 占位符列表)
        """
        logger.info("="*60)
        logger.info("Stage 1: GLM-4.6V-Flash OCR + 图片占位符")
        logger.info("="*60)

        pdf = fitz.open(pdf_path)
        total_pages = len(pdf)

        if max_pages:
            total_pages = min(total_pages, max_pages)

        logger.info(f"PDF文件: {pdf_path}")
        logger.info(f"总页数: {len(pdf)} (处理前 {total_pages} 页)")

        # OCR prompt（添加页眉页脚处理）
        prompt = """你是一个专业的OCR识别系统。请将这个PDF页面转换为Markdown格式。

## 输出格式要求
请使用以下格式输出：
```markdown
[你的Markdown内容]
```

## 转换规则

### 文字内容
- 标题：使用 # ## ### #### 表示层级
- 段落：直接输出文字，空行分隔
- 列表：使用 - 或 1.
- 表格：使用 Markdown表格语法
- 公式：行内用 $x^2$，独立用 $$\\frac{a}{b}$$

### 图片处理
遇到图片时使用：
![图片类型：简要说明。详细描述包括图中所有可见的文字、标注、数据、颜色、位置等关键信息](IMAGE_PLACEHOLDER)

### 页眉页脚处理 ⚠️ 重要
- **不要识别页眉页脚**：忽略页面顶部和底部的重复信息（如书名、章节号、页码等）
- **只识别正文内容**：专注于页面中间的主要内容区域
- 常见页眉页脚特征：
  * 页码："1"、"第1页"、"Page 1"、"- 1 -"等
  * 书名/章节：出现在每页顶部或底部的重复标题
  * 装饰线：上下边框线、分隔线等

### 质量要求
1. 不要遗漏任何文字或图片
2. 保持原文的逻辑顺序
3. 专业术语、数字、符号必须准确
4. 图片描述要详细具体"""

        all_markdown = []
        all_placeholders = []
        placeholder_index = 0

        for page_num in range(total_pages):
            logger.info(f"\n处理第 {page_num + 1}/{total_pages} 页...")

            # 渲染页面
            page = pdf[page_num]
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)

            temp_image = f'/tmp/ocr_page_{page_num + 1}.png'
            pix.save(temp_image)

            # 调用GLM-4.6V-Flash
            image_base64 = self.glm_processor.compress_image(temp_image, compression='medium')
            response = self.glm_processor.call_glm46v_api(
                image_base64,
                prompt,
                max_tokens=8192,
                retry_count=2
            )

            if 'error' in response:
                logger.error(f"  ❌ OCR失败: {response['error']}")
                continue

            # 提取Markdown
            raw_markdown = response['choices'][0]['message']['content']
            cleaned_markdown = self.extract_markdown_content(raw_markdown)

            # 提取占位符
            page_placeholders = self._extract_placeholders_from_markdown(
                cleaned_markdown,
                page_num,
                placeholder_index
            )
            all_placeholders.extend(page_placeholders)
            placeholder_index += len(page_placeholders)

            logger.info(f"  ✓ OCR完成，提取到 {len(page_placeholders)} 个图片占位符")

            all_markdown.append(cleaned_markdown)

            # 删除临时图片
            os.remove(temp_image)

        pdf.close()

        # 合并所有页面的Markdown（直接拼接，依靠标题层级组织结构）
        final_markdown = ''.join(all_markdown)

        logger.info(f"\n✅ Stage 1 完成!")
        logger.info(f"  总共识别: {len(all_markdown)} 页")
        logger.info(f"  图片占位符: {len(all_placeholders)} 个")

        return final_markdown, all_placeholders

    def _extract_placeholders_from_markdown(
        self,
        markdown: str,
        page_num: int,
        start_index: int
    ) -> List[Dict]:
        """从Markdown中提取图片占位符信息"""
        placeholders = []

        # 匹配格式: ![图片类型：说明...](IMAGE_PLACEHOLDER)
        pattern = r'!\[(.*?)\]\(IMAGE_PLACEHOLDER\)'
        matches = re.finditer(pattern, markdown)

        for i, match in enumerate(matches):
            desc = match.group(1)
            # 解析类型和描述
            if '：' in desc or ':' in desc:
                parts = re.split('[：:]', desc, 1)
                img_type = parts[0].strip()
                detailed_desc = parts[1].strip() if len(parts) > 1 else ''
            else:
                img_type = '图片'
                detailed_desc = desc

            placeholders.append({
                'index': start_index + i,
                'page': page_num + 1,
                'type': img_type,
                'description': detailed_desc,
                'full_match': match.group(0)
            })

        return placeholders

    # ============ Stage 2: 提取图片 ============

    def stage2_extract_images(
        self,
        pdf_path: str,
        output_dir: str,
        max_pages: int = None,
        dpi: int = 200
    ) -> List[Dict]:
        """Stage 2: 使用OpenCV提取所有图片"""
        logger.info("\n" + "="*60)
        logger.info("Stage 2: OpenCV 精确图片提取")
        logger.info("="*60)

        try:
            import cv2
            import numpy as np
        except ImportError:
            logger.error("❌ 需要安装 opencv-python: pip install opencv-python")
            return []

        pdf = fitz.open(pdf_path)
        total_pages = len(pdf)

        if max_pages:
            total_pages = min(total_pages, max_pages)

        images_dir = os.path.join(output_dir, 'extracted_images')
        os.makedirs(images_dir, exist_ok=True)

        all_images = []

        for page_num in range(total_pages):
            logger.info(f"\n提取第 {page_num + 1}/{total_pages} 页的图片...")

            # 渲染页面
            page = pdf[page_num]
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)

            page_image_path = os.path.join(output_dir, f'.temp_page_{page_num + 1}.png')
            pix.save(page_image_path)

            # 使用OpenCV检测图片
            images_info = self._detect_images_with_opencv(page_image_path, page_num + 1)

            # 裁剪并保存
            for idx, img_info in enumerate(images_info):
                bbox = img_info['bbox']
                filename = f'page_{page_num + 1:03d}_img_{idx + 1:02d}.png'
                output_path = os.path.join(images_dir, filename)

                if self._crop_image_from_page(page_image_path, bbox, output_path):
                    img_info['filename'] = filename
                    img_info['path'] = output_path
                    all_images.append(img_info)
                    logger.info(f"  ✓ 保存: {filename}")

            os.remove(page_image_path)

        pdf.close()

        logger.info(f"\n✅ Stage 2 完成! 提取了 {len(all_images)} 个图片")
        return all_images

    # ============ Stage 3: GLM-4V 图片描述 ============

    def stage3_describe_images(
        self,
        images: List[Dict]
    ) -> List[Dict]:
        """
        Stage 3: 使用GLM-4V描述所有提取的图片

        Args:
            images: 图片信息列表

        Returns:
            带描述的图片信息列表
        """
        logger.info("\n" + "="*60)
        logger.info("Stage 3: GLM-4V 图片描述生成")
        logger.info("="*60)

        for idx, img_info in enumerate(images):
            logger.info(f"\n描述图片 {idx + 1}/{len(images)}: {img_info['filename']}")

            description = self._describe_single_image(img_info['path'])
            img_info['description'] = description

            logger.info(f"  ✓ {description[:100]}...")

        logger.info(f"\n✅ Stage 3 完成! 描述了 {len(images)} 个图片")
        return images

    def _describe_single_image(self, image_path: str, max_size: int = 1920) -> str:
        """使用GLM-4V描述单张图片"""
        # 压缩图片
        img = Image.open(image_path)
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # 转换图片模式
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # 转换为JPEG字节流
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        image_bytes = buffer.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # 调用GLM-4V API
        prompt = """请详细描述这张图片的内容。

要求：
1. 识别图片的类型（几何图形、数学公式、统计图表、示意图、地图等）
2. 描述图片中的关键元素和细节
3. 如果有文字或标注，请准确引用
4. 描述要准确、简洁，不超过200字

请直接返回描述文本，不要添加其他内容。"""

        payload = {
            "model": "zai-org/glm-4.6v-flash",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }

        response = requests.post(
            f"{self.glm_api_url}/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.glm_api_key}"
            },
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        description = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

        return description

    # ============ Stage 4: DeepSeek 语义匹配 ============

    def stage4_match_placeholders(
        self,
        markdown: str,
        placeholders: List[Dict],
        image_descriptions: List[Dict]
    ) -> Dict[int, str]:
        """
        Stage 4: 使用DeepSeek进行语义匹配

        Args:
            markdown: 完整的Markdown文档
            placeholders: 占位符列表
            image_descriptions: 图片描述列表

        Returns:
            匹配映射: {placeholder_index: image_filename}
        """
        logger.info("\n" + "="*60)
        logger.info("Stage 4: DeepSeek 语义匹配")
        logger.info("="*60)

        logger.info(f"  占位符数量: {len(placeholders)}")
        logger.info(f"  图片数量: {len(image_descriptions)}")

        # 构建prompt
        prompt = f"""你是一个智能文档处理助手，负责将图片占位符与实际图片进行语义匹配。

## 任务说明
我会给你：
1. **完整的Markdown文档内容**（包含所有占位符及其上下文）
2. 一组实际图片的描述（由GLM-4V视觉模型生成）

请你**仔细阅读整个文档，理解每个占位符在文档中的上下文**，然后将占位符匹配到最合适的图片。

## 匹配原则
1. **上下文理解**：优先根据占位符在文档中的位置和内容来判断
2. **语义相似度**：占位符描述的内容应该与图片描述的内容高度一致
3. **细节匹配**：关键元素（如形状、标注、文字、数量等）必须匹配
4. **一一对应**：每个占位符匹配一个唯一的图片，**每个图片只能匹配一个占位符**
5. **不存在重复匹配**：如果多个占位符看起来相似，只选择第一个最合适的匹配
6. **精确匹配**：如果找不到合适的匹配，就返回null，不要强行匹配

## 完整Markdown文档

```
{markdown[:30000]}
```

## 占位符列表

"""

        for p in placeholders:
            prompt += f"\n**占位符 {p['index']}**\n"
            prompt += f"- 页码: {p['page']}\n"
            prompt += f"- 类型: {p.get('type', '未知')}\n"
            prompt += f"- 描述: {p.get('description', '')[:200]}...\n"

        prompt += "\n## 图片描述列表\n"

        for img in image_descriptions:
            prompt += f"\n**{img['filename']}**\n"
            prompt += f"- 描述: {img.get('description', '')[:300]}...\n"

        prompt += """

## 输出要求

请严格按照以下JSON格式输出：

```json
{
  "matches": [
    {
      "placeholder_index": 0,
      "image_filename": "image5.png",
      "confidence": "高",
      "reason": "根据文档上下文，这是数轴图，图片描述完全匹配"
    }
  ],
  "unmatched_placeholders": [1, 5],
  "unmatched_images": ["image10.png"]
}
```

现在请开始匹配：
"""

        # 调用DeepSeek API
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000,
            "response_format": {
                "type": "json_object"
            }
        }

        logger.info("  调用DeepSeek API...")

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        # 解析结果
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        try:
            match_result = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ 解析JSON失败: {e}")
            logger.error(f"  返回内容: {content[:500]}")
            return {}

        # 提取匹配映射
        matches = match_result.get('matches', [])
        mapping = {}

        for match in matches:
            placeholder_index = match.get('placeholder_index')
            image_filename = match.get('image_filename')
            if placeholder_index is not None and image_filename:
                mapping[placeholder_index] = image_filename
                logger.info(f"  ✓ 占位符 {placeholder_index} → {image_filename}")

        unmatched = match_result.get('unmatched_placeholders', [])
        if unmatched:
            logger.warning(f"  未匹配的占位符: {unmatched}")

        logger.info(f"\n✅ Stage 4 完成! 匹配了 {len(mapping)} 个占位符")
        return mapping

    # ============ Stage 5: 替换占位符 ============

    def stage5_replace_placeholders(
        self,
        markdown: str,
        placeholders: List[Dict],
        mapping: Dict[int, str],
        images_dir: str
    ) -> str:
        """
        Stage 5: 替换占位符为实际图片路径

        Args:
            markdown: Markdown文档
            placeholders: 占位符列表
            mapping: 匹配映射
            images_dir: 图片目录

        Returns:
            替换后的Markdown
        """
        logger.info("\n" + "="*60)
        logger.info("Stage 5: 替换占位符为图片路径")
        logger.info("="*60)

        # 按索引倒序替换（避免位置偏移）
        sorted_placeholders = sorted(placeholders, key=lambda x: x['index'], reverse=True)

        for placeholder in sorted_placeholders:
            idx = placeholder['index']
            full_match = placeholder['full_match']

            if idx in mapping:
                image_filename = mapping[idx]
                # 使用相对路径
                image_path = os.path.join('extracted_images', image_filename)

                # 替换占位符
                markdown = markdown.replace(full_match, f'![{placeholder.get("type", "图片")}]({image_path})')
                logger.info(f"  ✓ 替换占位符 {idx} → {image_path}")
            else:
                # 移除未匹配的占位符
                markdown = markdown.replace(full_match, '')
                logger.warning(f"  ⚠️  移除未匹配的占位符 {idx}")

        logger.info(f"\n✅ Stage 5 完成! 所有占位符已处理")
        return markdown

    # ============ 完整流程 ============

    def convert(
        self,
        pdf_path: str,
        output_dir: str,
        max_pages: int = None
    ) -> str:
        """
        完整转换流程

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            max_pages: 最大处理页数

        Returns:
            最终Markdown路径
        """
        logger.info("\n" + "="*70)
        logger.info("PDF → Markdown 完整转换流程")
        logger.info("="*70)
        logger.info(f"输入: {pdf_path}")
        logger.info(f"输出: {output_dir}")
        logger.info(f"页数限制: {max_pages or '全部'}")

        os.makedirs(output_dir, exist_ok=True)

        # Stage 1: OCR + 占位符
        markdown, placeholders = self.stage1_ocr_with_placeholders(pdf_path, max_pages)

        # Stage 1.5: DeepSeek排版优化（可选）
        if self.format_with_deepseek:
            markdown = self.format_markdown_with_deepseek(markdown)

        # 保存中间结果
        md_with_placeholders = os.path.join(output_dir, 'markdown_with_placeholders.md')
        with open(md_with_placeholders, 'w', encoding='utf-8') as f:
            f.write(markdown)
        logger.info(f"\n💾 保存: {md_with_placeholders}")

        # ⚡ 性能优化：如果没有图片占位符，跳过Stage 2-5
        if not placeholders:
            logger.info("\n" + "="*60)
            logger.info("⚡ 性能优化：未检测到图片占位符")
            logger.info("="*60)
            logger.info("✅ 跳过 Stage 2: OpenCV图片提取")
            logger.info("✅ 跳过 Stage 3: GLM-4V图片描述")
            logger.info("✅ 跳过 Stage 4: DeepSeek语义匹配")
            logger.info("✅ 跳过 Stage 5: 占位符替换")
            logger.info("\n🎉 转换完成！（纯文字文档，无需图片处理）")

            # 同时保存为final.md
            final_md_path = os.path.join(output_dir, 'final.md')
            with open(final_md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            logger.info(f"\n📄 最终Markdown: {final_md_path}")
            return final_md_path

        # Stage 2: 提取图片
        images = self.stage2_extract_images(pdf_path, output_dir, max_pages)

        if not images:
            logger.warning("\n⚠️  未提取到图片，跳过后续步骤")
            return md_with_placeholders

        # Stage 3: 描述图片
        images = self.stage3_describe_images(images)

        # Stage 4: 语义匹配
        mapping = self.stage4_match_placeholders(markdown, placeholders, images)

        # Stage 5: 替换占位符
        final_markdown = self.stage5_replace_placeholders(
            markdown,
            placeholders,
            mapping,
            output_dir
        )

        # 保存最终结果
        final_md_path = os.path.join(output_dir, 'final.md')
        with open(final_md_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)

        logger.info("\n" + "="*70)
        logger.info("✅ 转换完成！")
        logger.info("="*70)
        logger.info(f"最终Markdown: {final_md_path}")
        logger.info(f"提取的图片: {os.path.join(output_dir, 'extracted_images')}")
        logger.info(f"占位符数量: {len(placeholders)}")
        logger.info(f"匹配成功: {len(mapping)}")
        logger.info("="*70 + "\n")

        return final_md_path

    def _detect_images_with_opencv(self, page_image: str, page_num: int) -> List[Dict]:
        """使用OpenCV检测页面中的图片"""
        import cv2
        import numpy as np

        logger.info(f"  使用OpenCV检测图片区域...")

        # 读取图片
        img = cv2.imread(page_image)
        if img is None:
            logger.error(f"    ❌ 无法读取图片: {page_image}")
            return []

        height, width = img.shape[:2]
        logger.info(f"    页面尺寸: {width}x{height}")

        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 使用Canny边缘检测
        edges = cv2.Canny(gray, 50, 150)

        # 膨胀边缘
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)

        # 查找轮廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        images_info = []
        min_area = width * height * 0.02

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)

            # 扩展边界框
            padding = 10
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(width, x + w + padding)
            y2 = min(height, y + h + padding)

            # 检查是否可能是图片
            bbox_area = (x2 - x1) * (y2 - y1)
            aspect_ratio = (x2 - x1) / (y2 - y1) if (y2 - y1) > 0 else 0

            if bbox_area > width * height * 0.01 and 0.2 < aspect_ratio < 5:
                images_info.append({
                    "page": page_num,
                    "bbox": [x1, y1, x2, y2],
                    "type": "图片",
                    "description": ""
                })

        # 合并重叠的bbox
        if len(images_info) > 1:
            images_info = self._merge_overlapping_bboxes(images_info)

        logger.info(f"    ✓ 检测到 {len(images_info)} 个图片区域")
        return images_info

    def _merge_overlapping_bboxes(self, images_info: List[Dict]) -> List[Dict]:
        """合并重叠或相邻的边界框"""
        if not images_info:
            return []

        sorted_info = sorted(images_info, key=lambda x: x['bbox'][0])
        merged = [sorted_info[0]]

        for current in sorted_info[1:]:
            last = merged[-1]
            last_bbox = last['bbox']
            curr_bbox = current['bbox']

            if (curr_bbox[0] < last_bbox[2] + 50 and
                curr_bbox[1] < last_bbox[3] + 50):

                new_bbox = [
                    min(last_bbox[0], curr_bbox[0]),
                    min(last_bbox[1], curr_bbox[1]),
                    max(last_bbox[2], curr_bbox[2]),
                    max(last_bbox[3], curr_bbox[3])
                ]
                last['bbox'] = new_bbox
            else:
                merged.append(current)

        return merged

    def _crop_image_from_page(
        self,
        page_image_path: str,
        bbox: List[int],
        output_path: str
    ) -> bool:
        """从页面图片中裁剪出指定区域"""
        try:
            page_img = Image.open(page_image_path)
            width, height = page_img.size

            x1, y1, x2, y2 = bbox

            # 验证bbox
            if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
                logger.warning(f"    ⚠️  bbox超出页面范围: {bbox}, 页面尺寸: {width}x{height}")
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)

            # 裁剪图片
            cropped = page_img.crop((x1, y1, x2, y2))

            # 保存
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cropped.save(output_path, 'PNG', quality=95)

            return True

        except Exception as e:
            logger.error(f"    ❌ 裁剪失败: {e}")
            return False


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PDF转Markdown（完整版）- 整合OCR、图片提取、语义匹配'
    )
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('-o', '--output', default='./output_complete', help='输出目录')
    parser.add_argument('-n', '--max-pages', type=int, help='最大处理页数（用于测试）')
    parser.add_argument('--format-with-deepseek', action='store_true',
                        help='启用DeepSeek-chat进行排版优化（Stage 1.5）')

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"❌ 文件不存在: {args.pdf_path}")
        return 1

    # 创建转换器
    converter = CompletePDFConverter(format_with_deepseek=args.format_with_deepseek)

    # 执行完整转换
    try:
        final_md_path = converter.convert(
            args.pdf_path,
            args.output,
            args.max_pages
        )

        print(f"\n🎉 转换成功！")
        print(f"   输出文件: {final_md_path}")

        return 0

    except Exception as e:
        logger.error(f"\n❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
