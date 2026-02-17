"""
识别模块：内容提取
针对每个元素框，调用视觉模型进行内容识别和结构化提取
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from PIL import Image
import fitz  # PyMuPDF

from utils import (
    call_vision_api,
    save_json,
    load_json,
    load_config
)


class ContentExtractor:
    """内容提取器"""

    # 文本类元素提取Prompt
    TEXT_EXTRACTION_PROMPT = """提取图片中的所有文字，按原文顺序输出。

要求：
- 直接输出文字，不要任何解释
- 保持换行和段落结构
- 保留所有符号和数字

输出文字："""

    # 公式提取Prompt
    FORMULA_EXTRACTION_PROMPT = """将图片中的数学公式转换为LaTeX代码。

直接输出LaTeX代码，不要任何解释。"""

    # 表格提取Prompt
    TABLE_EXTRACTION_PROMPT = """提取表格内容，输出JSON格式：

{
  "headers": ["列1", "列2"],
  "rows": [
    {"cells": ["数据1", "数据2"]},
    {"cells": ["数据3", "数据4"]}
  ]
}

直接输出JSON，不要任何解释。"""

    # 图片描述Prompt
    IMAGE_DESCRIPTION_PROMPT = """用一句话描述这张图片的内容（10-20字）。

直接输出描述，不要任何解释。"""

    def __init__(
        self,
        api_url: str = "http://192.168.100.110:9999/v1/chat/completions",
        api_key: str = "sk-test-key",
        model: str = "glm-4.6v-flash",
        element_mapping_file: str = "config/element_mapping.yaml"
    ):
        """
        初始化内容提取器

        Args:
            api_url: 本地视觉模型API端点
            api_key: API密钥
            model: 模型名称
            element_mapping_file: 元素类型映射文件
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.element_config = load_config(element_mapping_file)

    def extract_page_content(
        self,
        layout_data: Dict,
        pdf_path: str,
        output_dir: Optional[str] = None
    ) -> Optional[Dict]:
        """
        提取单个页面的所有元素内容

        Args:
            layout_data: 版面分析数据（page_layout.json）
            pdf_path: PDF文件路径
            output_dir: 输出目录

        Returns:
            内容提取结果字典，失败返回None
        """
        page_num = layout_data['page_info']['page_number']
        print(f"\n提取第 {page_num} 页内容...")
        print("=" * 60)

        # 1. 加载PDF页面图片
        print("  步骤1: 加载PDF页面图片...")
        try:
            pdf_doc = fitz.open(pdf_path)
            page = pdf_doc[page_num - 1]
            dpi = layout_data['page_info']['dpi']
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # 转换为PIL图片
            import io
            img_data = pix.tobytes("PNG")
            page_image = Image.open(io.BytesIO(img_data))
            page_width, page_height = page_image.size
            pdf_doc.close()

            print(f"  成功: 页面图片 {page_width}x{page_height}")

        except Exception as e:
            print(f"  错误: 无法加载PDF页面 - {e}")
            return None

        # 2. 裁剪元素图片并提取内容
        print("  步骤2: 裁剪元素并提取内容...")
        elements = layout_data.get('elements', [])
        extracted_elements = []

        for idx, element in enumerate(elements):
            elem_type = element['type']
            elem_id = element['element_id']
            bbox = element['bbox']

            print(f"  处理元素 {idx + 1}/{len(elements)}: {elem_type} ({elem_id})")

            try:
                # 裁剪元素图片
                elem_image = self._crop_element(page_image, bbox)

                # 根据元素类型提取内容
                if elem_type in ['title_h1', 'title_h2', 'title_h3', 'title_h4', 'title_h5', 'title_h6', 'paragraph']:
                    content = self._extract_text_content(elem_image, element)
                    element['content'] = content
                    element['extraction_quality'] = {'content_confidence': 0.9, 'formatting_preserved': True}

                elif elem_type in ['ordered_list', 'unordered_list']:
                    content = self._extract_list_content(elem_image, element)
                    element['list_items'] = content
                    element['extraction_quality'] = {'content_confidence': 0.85, 'formatting_preserved': True}

                elif elem_type in ['formula_inline', 'formula_block']:
                    latex_code = self._extract_formula(elem_image)
                    element['latex_code'] = latex_code
                    element['formula_alt'] = latex_code  # 用于alt属性
                    element['extraction_quality'] = {'content_confidence': 0.9, 'formatting_preserved': True}

                elif elem_type == 'table':
                    table_data = self._extract_table(elem_image, element)
                    element['table_data'] = table_data
                    element['extraction_quality'] = {'content_confidence': 0.85, 'formatting_preserved': True}

                elif elem_type == 'image':
                    image_data = self._extract_image(elem_image, element)
                    element['image_data'] = image_data
                    element['extraction_quality'] = {'content_confidence': 0.95, 'formatting_preserved': True}

                elif elem_type == 'caption':
                    content = self._extract_caption(elem_image)
                    element['caption_text'] = content
                    element['extraction_quality'] = {'content_confidence': 0.9, 'formatting_preserved': True}

                else:
                    # header/footer等其他类型
                    content = self._extract_text_content(elem_image, element)
                    element['content'] = content
                    element['extraction_quality'] = {'content_confidence': 0.8, 'formatting_preserved': True}

                print(f"    ✓ 提取成功")

            except Exception as e:
                print(f"    ✗ 提取失败: {e}")
                element['extraction_error'] = str(e)
                element['extraction_quality'] = {'content_confidence': 0.0, 'formatting_preserved': False}

            extracted_elements.append(element)

        # 3. 构建输出数据
        print("  步骤3: 构建输出数据...")
        result = {
            # 继承所有版面分析字段
            **layout_data,

            # 扩展元素内容
            'elements': extracted_elements,

            # 页面汇总信息
            'page_summary': self._generate_summary(extracted_elements),

            # 处理日志
            'extraction_log': {
                'api_calls': len(extracted_elements),
                'total_tokens': 0,  # TODO: 统计token使用
                'processing_time': 0,  # TODO: 记录处理时间
                'retry_count': 0,
                'failed_elements': [
                    e['element_id'] for e in extracted_elements
                    if 'extraction_error' in e
                ]
            }
        }

        # 4. 保存结果
        if output_dir:
            output_file = Path(output_dir) / f"page_content_{page_num:04d}.json"
            save_json(result, str(output_file))
            print(f"  结果已保存: {output_file}")

        print("  ✓ 内容提取完成")
        return result

    def _crop_element(
        self,
        page_image: Image.Image,
        bbox: List[int],
        padding: int = 5
    ) -> Image.Image:
        """
        从页面图片中裁剪元素区域

        Args:
            page_image: 页面图片
            bbox: 边界框 [x1, y1, x2, y2]
            padding: 扩展边距（像素）

        Returns:
            裁剪后的元素图片
        """
        x1, y1, x2, y2 = bbox

        # 添加边距
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(page_image.width, x2 + padding)
        y2 = min(page_image.height, y2 + padding)

        # 裁剪
        element_image = page_image.crop((x1, y1, x2, y2))
        return element_image

    def _clean_model_response(self, response: str) -> str:
        """
        清理GLM模型的响应，移除思考标签

        Args:
            response: 原始响应文本

        Returns:
            清理后的响应文本
        """
        if not response:
            return response

        content = response.strip()

        # 移除 <|beginofthink|>...<|endofthink|> 标签及其内容
        content = re.sub(r'<\|beginofthink\|>.*?<\|endofthink\|>', '', content, flags=re.DOTALL)

        # 移除 <|beginofbox|>...<|endofbox|> 标签及其内容
        content = re.sub(r'<\|beginofbox\|>.*?<\|endofbox\|>', '', content, flags=re.DOTALL)

        # 移除其他可能的思考标记
        content = re.sub(r'<\|.*?\|>', '', content)

        # 移除可能的前缀
        content = re.sub(r'^(以下是|以下是提取的|内容|文本|提取内容)[:：]\s*', '', content)
        content = re.sub(r'^```[a-z]*\n', '', content)
        content = re.sub(r'\n```$', '', content)

        return content.strip()

    def _extract_text_content(
        self,
        element_image: Image.Image,
        element: Dict
    ) -> str:
        """提取文本内容"""
        response = call_vision_api(
            api_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
            image=element_image,
            prompt=self.TEXT_EXTRACTION_PROMPT,
            max_tokens=4096,
            temperature=0.1
        )

        if not response:
            return ""

        # 清理响应
        return self._clean_model_response(response)

    def _extract_list_content(
        self,
        element_image: Image.Image,
        element: Dict
    ) -> List[Dict]:
        """提取列表内容"""
        response = call_vision_api(
            api_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
            image=element_image,
            prompt=self.TEXT_EXTRACTION_PROMPT,
            max_tokens=4096,
            temperature=0.1
        )

        if not response:
            return []

        # 解析列表结构（简单实现）
        content = response.strip()
        lines = content.split('\n')
        list_items = []

        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 移除编号
            line = re.sub(r'^[\d]+\s*[\.\)、]\s*', '', line)
            line = re.sub(r'^[A-Za-z]\s*[\.\)、]\s*', '', line)
            line = re.sub(r'^[●■◆]\s*', '', line)

            list_items.append({
                'item_id': f"li_{idx + 1:03d}",
                'content': line,
                'child_items': []
            })

        return list_items

    def _extract_formula(
        self,
        element_image: Image.Image
    ) -> str:
        """提取公式LaTeX代码"""
        response = call_vision_api(
            api_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
            image=element_image,
            prompt=self.FORMULA_EXTRACTION_PROMPT,
            max_tokens=2048,
            temperature=0.1
        )

        if not response:
            return ""

        # 清理响应
        latex = response.strip()
        latex = re.sub(r'^```[a-z]*\n', '', latex)
        latex = re.sub(r'\n```$', '', latex)
        latex = latex.replace('$$', '').replace('$', '')

        return latex

    def _extract_table(
        self,
        element_image: Image.Image,
        element: Dict
    ) -> Dict:
        """提取表格数据"""
        response = call_vision_api(
            api_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
            image=element_image,
            prompt=self.TABLE_EXTRACTION_PROMPT,
            max_tokens=4096,
            temperature=0.1
        )

        if not response:
            return {
                'headers': [],
                'rows': [],
                'table_style': {'border_width': '1pt', 'cell_padding': '4pt'}
            }

        # 解析JSON响应
        try:
            # 提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.strip()

            table_data = json.loads(json_str)

            # 添加默认样式
            if 'table_style' not in table_data:
                table_data['table_style'] = {
                    'border_width': '1pt',
                    'cell_padding': '4pt'
                }

            return table_data

        except Exception as e:
            print(f"    警告: 解析表格JSON失败 - {e}")
            return {
                'headers': [],
                'rows': [],
                'table_style': {'border_width': '1pt', 'cell_padding': '4pt'}
            }

    def _extract_image(
        self,
        element_image: Image.Image,
        element: Dict
    ) -> Dict:
        """提取图片数据和描述"""
        # 1. 生成描述
        description = call_vision_api(
            api_url=self.api_url,
            api_key=self.api_key,
            model=self.model,
            image=element_image,
            prompt=self.IMAGE_DESCRIPTION_PROMPT,
            max_tokens=512,
            temperature=0.3
        )

        if not description:
            description = "图片"

        # 2. 转换为base64
        import base64
        import io
        buffer = io.BytesIO()
        element_image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        base64_data = base64.b64encode(img_bytes).decode('utf-8')

        return {
            'base64_data': base64_data,
            'format': 'PNG',
            'width': element_image.width,
            'height': element_image.height,
            'alt_text': description.strip()
        }

    def _extract_caption(
        self,
        element_image: Image.Image
    ) -> str:
        """提取图注/表注"""
        return self._extract_text_content(element_image, {})

    def _generate_summary(self, elements: List[Dict]) -> Dict:
        """生成页面汇总信息"""
        type_counts = {}
        for elem in elements:
            elem_type = elem['type']
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1

        return {
            'total_elements': len(elements),
            'element_type_counts': type_counts,
            'has_formulas': any(t in ['formula_inline', 'formula_block'] for t in type_counts.keys()),
            'has_tables': 'table' in type_counts,
            'has_images': 'image' in type_counts,
            'word_count_estimate': sum(
                len(e.get('content', '').split())
                for e in elements
                if 'content' in e
            )
        }


if __name__ == "__main__":
    # 测试代码
    print("识别模块测试")
    print("=" * 60)

    # 配置
    API_URL = "http://localhost:9999/v1/chat/completions"
    API_KEY = "sk-test-key"
    MODEL = "zai-org/glm-4.6v-flash"

    extractor = ContentExtractor(
        api_url=API_URL,
        api_key=API_KEY,
        model=MODEL
    )

    # 测试单页
    layout_file = "output_layout_test/page_layout_0012.json"
    test_pdf = "input_file/正文26春初中非常课课通数学8年级人教.pdf"

    if os.path.exists(layout_file) and os.path.exists(test_pdf):
        print(f"\n测试文件: {test_pdf}")
        layout_data = load_json(layout_file)

        if layout_data:
            result = extractor.extract_page_content(
                layout_data=layout_data,
                pdf_path=test_pdf,
                output_dir="output_content_test"
            )

            if result:
                print(f"\n提取成功!")
                print(f"总元素数: {result['page_summary']['total_elements']}")
                print(f"元素类型分布: {result['page_summary']['element_type_counts']}")
    else:
        print(f"测试文件不存在: {layout_file} 或 {test_pdf}")
        print("请先运行画框模块生成版面分析数据")
