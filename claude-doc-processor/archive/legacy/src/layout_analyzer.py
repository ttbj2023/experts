"""
画框模块：版面分析
使用视觉模型分析PDF页面的版面结构，输出元素框和类型信息
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from PIL import Image
import yaml

from utils import (
    pdf_to_images,
    call_vision_api,
    save_json,
    load_json,
    validate_bbox,
    check_overlap,
    load_config
)


class LayoutAnalyzer:
    """版面分析器"""

    # 版面分析专用Prompt
    LAYOUT_ANALYSIS_PROMPT = """这是一个图像分割任务。请用矩形框分割这张图片中的所有内容块。

**任务说明**：
把图片看作一个整体，用矩形框框出视觉上独立的"块"。就像切蛋糕一样，把页面切分成若干个矩形区域。

**分割规则**：

1. **什么是"块"**：
   - 视觉上聚集在一起的内容
   - 周围有空白包围的区域
   - 自然的内容边界（由空白、线条、颜色区分）

2. **不要考虑内容类型**：
   - 不需要判断是"文字"、"图片"、"公式"还是"表格"
   - 只需要识别"这是一块内容"
   - 让矩形框自然地包围视觉内容

3. **颗粒度控制**：
   - 块的大小适中：不要太大（包含多个独立内容），也不要太小（切分到单行）
   - 如果多个文字行紧挨着（间距很小），应该框在一起作为一个块
   - 图片/图表通常是一个完整的块

4. **典型块的例子**：
   - 一组紧密排列的文字段落 = 一个矩形
   - 一张图片 = 一个矩形
   - 一个表格 = 一个矩形
   - 一个大标题 = 一个矩形

5. **输出格式**：为每个块分配编号（1,2,3...），输出JSON：

```json
{
  "elements": [
    {
      "element_id": "block_001",
      "bbox": [x1, y1, x2, y2],
      "read_order": 1
    }
  ]
}
```

6. **坐标说明**：
   - bbox: [x1, y1, x2, y2]，包围这个块的最小矩形
   - (0,0)在左上角

请开始分割，仅输出JSON格式结果。"""

    def __init__(
        self,
        api_url: str = "http://192.168.100.110:9999/v1/chat/completions",
        api_key: str = "sk-test-key",
        model: str = "glm-4.6v-flash",
        element_mapping_file: str = "config/element_mapping.yaml"
    ):
        """
        初始化版面分析器

        Args:
            api_url: API端点URL
            api_key: API密钥
            model: 模型名称
            element_mapping_file: 元素类型映射文件
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.element_config = load_config(element_mapping_file)

        # 从配置中提取允许的元素类型
        if self.element_config:
            self.allowed_types = list(
                self.element_config.get('validation_rules', {}).get('allowed_types', [])
            )
        else:
            # 默认允许的类型
            self.allowed_types = [
                'title_h1', 'title_h2', 'title_h3', 'title_h4', 'title_h5', 'title_h6',
                'paragraph', 'ordered_list', 'unordered_list',
                'formula_inline', 'formula_block', 'table', 'image',
                'header', 'footer', 'caption'
            ]

    def analyze_page(
        self,
        pdf_path: str,
        page_num: int,
        dpi: int = 200,
        output_dir: Optional[str] = None
    ) -> Optional[Dict]:
        """
        分析单个PDF页面的版面结构

        Args:
            pdf_path: PDF文件路径
            page_num: 页码（从1开始）
            dpi: 渲染DPI
            output_dir: 输出目录（保存中间结果）

        Returns:
            版面分析结果字典，失败返回None
        """
        print(f"\n处理第 {page_num} 页...")
        print("=" * 60)

        # 1. PDF转图片
        print("  步骤1: PDF转高清图片...")
        try:
            images = pdf_to_images(pdf_path, dpi=dpi, pages=[page_num])
            if not images:
                print(f"  错误: 无法转换第 {page_num} 页")
                return None

            _, page_image = images[0]
            page_width, page_height = page_image.size
            print(f"  成功: 图片尺寸 {page_width}x{page_height} 像素")

            # 保存图片（用于调试）
            if output_dir:
                debug_dir = Path(output_dir) / "debug_images"
                debug_dir.mkdir(parents=True, exist_ok=True)
                page_image.save(debug_dir / f"page_{page_num:04d}.png")
                print(f"  调试图片已保存: {debug_dir / f'page_{page_num:04d}.png'}")

        except Exception as e:
            print(f"  错误: PDF转图片失败 - {e}")
            return None

        # 2. 调用视觉模型分析版面
        print("  步骤2: 调用视觉模型进行版面分析...")
        try:
            model_response = call_vision_api(
                api_url=self.api_url,
                api_key=self.api_key,
                model=self.model,
                image=page_image,
                prompt=self.LAYOUT_ANALYSIS_PROMPT,
                max_tokens=8192,
                temperature=0.1,
                max_retries=3
            )

            if not model_response:
                print("  错误: 视觉模型API调用失败")
                return None

            print("  成功: 获得模型响应")

        except Exception as e:
            print(f"  错误: 视觉模型调用异常 - {e}")
            return None

        # 3. 解析模型输出
        print("  步骤3: 解析模型输出...")
        try:
            parsed_data = self._parse_layout_response(
                model_response,
                page_width,
                page_height,
                page_num
            )
            print(f"  成功: 识别到 {len(parsed_data['elements'])} 个元素")

        except Exception as e:
            print(f"  错误: 解析模型输出失败 - {e}")
            # 保存原始响应用于调试
            if output_dir:
                debug_dir = Path(output_dir) / "debug_responses"
                debug_dir.mkdir(parents=True, exist_ok=True)
                with open(debug_dir / f"page_{page_num:04d}_raw.txt", 'w', encoding='utf-8') as f:
                    f.write(model_response)
                print(f"  原始响应已保存: {debug_dir / f'page_{page_num:04d}_raw.txt'}")
            return None

        # 4. 验证版面分析结果
        print("  步骤4: 验证版面分析结果...")
        validation_result = self._validate_layout(parsed_data, page_width, page_height)

        if not validation_result['valid']:
            print(f"  警告: 版面分析存在以下问题:")
            for issue in validation_result['issues']:
                print(f"    - {issue}")
            # 不中断流程，继续处理

        # 5. 保存结果
        if output_dir:
            output_file = Path(output_dir) / f"page_layout_{page_num:04d}.json"
            save_json(parsed_data, str(output_file))
            print(f"  结果已保存: {output_file}")

        print("  ✓ 版面分析完成")
        return parsed_data

    def _parse_layout_response(
        self,
        response: str,
        page_width: int,
        page_height: int,
        page_num: int
    ) -> Dict:
        """
        解析视觉模型的响应文本

        Args:
            response: 模型响应文本
            page_width: 页面宽度
            page_height: 页面高度
            page_num: 页码

        Returns:
            解析后的数据字典
        """
        # 清理GLM模型的思考标签（使用已验证有效的方式）
        # 移除 <|beginofthink|>...<|endofthink|> 标签及其内容
        response = re.sub(r'<\|beginofthink\|>.*?<\|endofthink\|>', '', response, flags=re.DOTALL)

        # 移除 <|beginofbox|>...<|endofbox|> 标签及其内容
        response = re.sub(r'<\|beginofbox\|>.*?<\|endofbox\|>', '', response, flags=re.DOTALL)

        # 移除其他可能的思考标记
        response = re.sub(r'<\|.*?\|>', '', response)

        # 提取JSON（处理可能的markdown代码块）
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接提取JSON对象（从第一个{到最后一个}）
            # 使用正则匹配最外层的{...}
            json_match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("无法从响应中提取JSON")

        # 解析JSON
        data = json.loads(json_str)

        # 后处理：合并相邻的小元素（颗粒度优化）
        elements = data.get("elements", [])
        merged_elements = self._merge_small_elements(elements, page_width, page_height)
        data["elements"] = merged_elements

        # 构建标准输出格式
        result = {
            "document_info": {
                "source_file": "",  # 由外部填充
                "total_pages": 1,
                "processed_page": page_num,
                "processing_timestamp": datetime.now().isoformat()
            },
            "page_info": {
                "page_id": f"page_{page_num:03d}",
                "page_number": page_num,
                "page_size": {
                    "width": page_width,
                    "height": page_height,
                    "unit": "px"
                },
                "dpi": 200,
                "rotation": 0
            },
            "elements": [],
            "layout_info": data.get("layout_info", {
                "column_count": 1,
                "has_header": False,
                "has_footer": False
            }),
            "processing_status": {
                "success": True,
                "warnings": [],
                "errors": [],
                "model_used": self.model
            }
        }

        # 处理元素列表
        for idx, elem in enumerate(data.get("elements", [])):
            # 为新的简化格式添加默认字段
            if 'type' not in elem:
                elem['type'] = 'content_block'  # 默认类型

            if 'layout_attr' not in elem:
                # 推断layout_attr
                bbox = elem.get('bbox', [0, 0, 0, 0])
                width = bbox[2] - bbox[0]
                page_center = page_width / 2

                elem['layout_attr'] = {
                    'column': 'left' if bbox[0] < page_center else 'right',
                    'cross_column': width > page_width * 0.8,
                    'align': 'left'
                }

            # 构建元素对象
            element = {
                "element_id": elem.get("element_id", f"elem_{idx + 1:03d}"),
                "type": elem.get("type", "content_block"),
                "read_order": elem.get("read_order", idx + 1),
                "bbox": elem.get("bbox", [0, 0, 0, 0]),
                "layout_attr": elem.get("layout_attr", {}),
                "confidence": {
                    "type_detection": 0.9,
                    "bbox_accuracy": 0.85
                },
                "metadata": {
                    "area": 0,
                    "aspect_ratio": 0,
                    "position": "middle"
                }
            }

            # 计算元数据
            bbox = element["bbox"]
            if validate_bbox(bbox, page_width, page_height):
                x1, y1, x2, y2 = bbox
                element["metadata"]["area"] = (x2 - x1) * (y2 - y1)
                element["metadata"]["aspect_ratio"] = (x2 - x1) / (y2 - y1) if (y2 - y1) > 0 else 0

                # 判断位置
                if y1 < page_height * 0.3:
                    element["metadata"]["position"] = "top"
                elif y1 > page_height * 0.7:
                    element["metadata"]["position"] = "bottom"
                else:
                    element["metadata"]["position"] = "middle"

            result["elements"].append(element)

        return result

    def _merge_small_elements(
        self,
        elements: List[Dict],
        page_width: int,
        page_height: int
    ) -> List[Dict]:
        """
        合并相邻的小元素（颗粒度优化）

        Args:
            elements: 元素列表
            page_width: 页面宽度
            page_height: 页面高度

        Returns:
            合并后的元素列表
        """
        if not elements:
            return elements

        # 当前新Prompt已经产生较大的块，暂时不做合并
        # 只在元素非常小且垂直紧邻时才合并
        merged = []
        i = 0

        while i < len(elements):
            current = elements[i]
            current_bbox = current['bbox']
            current_height = current_bbox[3] - current_bbox[1]

            # 如果当前元素高度小于30px，尝试与下一个元素合并
            if current_height < 30 and i + 1 < len(elements):
                next_elem = elements[i + 1]
                next_bbox = next_elem['bbox']

                # 检查是否垂直紧邻（间隙小于20px）
                vertical_gap = next_bbox[1] - current_bbox[3]
                horizontal_overlap = not (current_bbox[2] < next_bbox[0] or next_bbox[2] < current_bbox[0])

                if vertical_gap < 20 and horizontal_overlap:
                    # 合并两个元素
                    merged_bbox = [
                        min(current_bbox[0], next_bbox[0]),
                        min(current_bbox[1], next_bbox[1]),
                        max(current_bbox[2], next_bbox[2]),
                        max(current_bbox[3], next_bbox[3])
                    ]

                    merged_elem = {
                        'element_id': current['element_id'],
                        'bbox': merged_bbox,
                        'read_order': current['read_order']
                    }
                    merged.append(merged_elem)
                    i += 2  # 跳过下一个元素
                    continue

            # 不合并，直接添加
            merged.append(current)
            i += 1

        return merged

    def _validate_layout(
        self,
        layout_data: Dict,
        page_width: int,
        page_height: int
    ) -> Dict:
        """
        验证版面分析结果

        Args:
            layout_data: 版面分析数据
            page_width: 页面宽度
            page_height: 页面高度

        Returns:
            验证结果 {"valid": bool, "issues": List[str]}
        """
        issues = []
        elements = layout_data.get("elements", [])

        # 1. 检查元素数量
        if len(elements) == 0:
            issues.append("未识别到任何元素")

        # 2. 检查阅读顺序连续性
        read_orders = [elem.get("read_order", 0) for elem in elements]
        if sorted(read_orders) != list(range(1, len(read_orders) + 1)):
            issues.append("阅读顺序不连续或重复")

        # 3. 检查边界框合法性
        for idx, elem in enumerate(elements):
            bbox = elem.get("bbox", [])
            if not validate_bbox(bbox, page_width, page_height):
                issues.append(f"元素 {idx + 1} 的边界框非法: {bbox}")

        # 4. 检查重叠框
        overlaps = check_overlap(elements, iou_threshold=0.5)
        if overlaps:
            for i, j in overlaps:
                issues.append(
                    f"元素 {i + 1} 和元素 {j + 1} 存在重叠 "
                    f"(IoU={calculate_iou(elements[i]['bbox'], elements[j]['bbox']):.2f})"
                )

        # 5. 检查必填字段
        required_fields = ["element_id", "type", "bbox", "read_order"]
        for idx, elem in enumerate(elements):
            missing_fields = [f for f in required_fields if f not in elem]
            if missing_fields:
                issues.append(f"元素 {idx + 1} 缺少字段: {missing_fields}")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

    def analyze_pdf(
        self,
        pdf_path: str,
        pages: Optional[List[int]] = None,
        output_dir: Optional[str] = None,
        dpi: int = 200
    ) -> List[Dict]:
        """
        分析多页PDF的版面结构

        Args:
            pdf_path: PDF文件路径
            pages: 要分析的页码列表（None表示全部）
            output_dir: 输出目录
            dpi: 渲染DPI

        Returns:
            每页的版面分析结果列表
        """
        # 获取总页数
        if pages is None:
            pdf_doc = fitz.open(pdf_path)
            total_pages = pdf_doc.page_count
            pdf_doc.close()
            pages = range(1, total_pages + 1)

        print(f"\n开始分析PDF: {pdf_path}")
        print(f"总页数: {len(pages)}")
        print("=" * 60)

        results = []
        for page_num in pages:
            result = self.analyze_page(
                pdf_path=pdf_path,
                page_num=page_num,
                dpi=dpi,
                output_dir=output_dir
            )

            if result:
                result['document_info']['source_file'] = pdf_path
                result['document_info']['total_pages'] = len(pages)
                results.append(result)

        print(f"\n{'=' * 60}")
        print(f"版面分析完成: 成功处理 {len(results)}/{len(pages)} 页")
        print("=" * 60)

        return results


def calculate_iou(bbox1: List[int], bbox2: List[int]) -> float:
    """计算两个边界框的交并比"""
    from utils import calculate_iou as _calc_iou
    return _calc_iou(bbox1, bbox2)


if __name__ == "__main__":
    # 测试代码
    print("画框模块测试")
    print("=" * 60)

    # 配置
    API_URL = os.getenv("VISION_API_URL", "http://192.168.100.110:9999/v1/chat/completions")
    API_KEY = os.getenv("VISION_API_KEY", "sk-test-key")
    MODEL = os.getenv("VISION_MODEL", "zai-org/glm-4.6v-flash")

    analyzer = LayoutAnalyzer(
        api_url=API_URL,
        api_key=API_KEY,
        model=MODEL
    )

    # 测试单页
    test_pdf = "input_file/正文26春初中非常课课通数学8年级人教.pdf"
    if os.path.exists(test_pdf):
        print(f"\n测试文件: {test_pdf}")
        result = analyzer.analyze_page(
            pdf_path=test_pdf,
            page_num=12,
            output_dir="output_layout_test"
        )

        if result:
            print(f"\n识别到 {len(result['elements'])} 个元素:")
            for elem in result['elements'][:5]:  # 打印前5个
                print(f"  - {elem['type']}: {elem['bbox']} (顺序: {elem['read_order']})")
