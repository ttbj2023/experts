"""
工具函数模块
提供PDF处理、图片处理、API调用等通用功能
"""

import os
import base64
import json
import time
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io
import requests


def load_config(config_file: str = "config/element_mapping.yaml") -> Dict:
    """
    加载YAML配置文件

    Args:
        config_file: 配置文件路径

    Returns:
        配置字典
    """
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("警告: PyYAML未安装，使用默认配置")
        return {}


def pdf_to_images(
    pdf_path: str,
    dpi: int = 200,
    output_format: str = "PNG",
    pages: Optional[List[int]] = None
) -> List[Tuple[int, Image.Image]]:
    """
    将PDF转换为高清图片

    Args:
        pdf_path: PDF文件路径
        dpi: 渲染DPI（默认200）
        output_format: 输出格式（PNG/JPEG）
        pages: 要转换的页码列表（None表示全部）

    Returns:
        [(页码, PIL图片对象), ...] 列表
    """
    pdf_doc = fitz.open(pdf_path)
    images = []

    # 如果未指定页码，处理所有页
    if pages is None:
        pages = range(1, pdf_doc.page_count + 1)

    for page_num in pages:
        page = pdf_doc[page_num - 1]  # fitz页码从0开始

        # 设置缩放因子（DPI转换）
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        # 渲染页面为图片
        pix = page.get_pixmap(matrix=mat)

        # 转换为PIL图片
        img_data = pix.tobytes(output_format)
        img = Image.open(io.BytesIO(img_data))

        images.append((page_num, img))

    pdf_doc.close()
    return images


def compress_image(
    image: Image.Image,
    max_width: int = 1280,
    quality: int = 85
) -> Image.Image:
    """
    压缩图片以适应API限制

    Args:
        image: PIL图片对象
        max_width: 最大宽度（像素）
        quality: JPEG质量（1-100）

    Returns:
        压缩后的PIL图片对象
    """
    # 计算缩放比例
    width, height = image.size
    if width > max_width:
        scale_ratio = max_width / width
        new_width = max_width
        new_height = int(height * scale_ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 转换为RGB模式（如果是RGBA）
    if image.mode != 'RGB':
        image = image.convert('RGB')

    return image


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    将PIL图片转换为base64编码

    Args:
        image: PIL图片对象
        format: 图片格式（PNG/JPEG）

    Returns:
        base64编码字符串
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    img_bytes = buffer.getvalue()
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    return base64_str


def call_vision_api(
    api_url: str,
    api_key: str,
    model: str,
    image: Image.Image,
    prompt: str,
    max_tokens: int = 8192,
    temperature: float = 0.1,
    max_retries: int = 3
) -> Optional[str]:
    """
    调用本地视觉模型API（OpenAI格式）

    Args:
        api_url: API端点URL
        api_key: API密钥
        model: 模型名称
        image: PIL图片对象
        prompt: 提示词
        max_tokens: 最大token数
        temperature: 温度参数
        max_retries: 最大重试次数

    Returns:
        模型响应文本，失败返回None
    """
    # 压缩图片
    compressed_image = compress_image(image)
    base64_image = image_to_base64(compressed_image, format="JPEG")

    # 构建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    # 重试机制
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']
            return content

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400 and attempt < max_retries - 1:
                # 400错误可能是图片太大，进一步压缩
                print(f"  400错误，尝试降低图片质量（重试 {attempt + 1}/{max_retries}）...")
                compressed_image = compress_image(
                    image,
                    max_width=int(1280 * (0.7 ** (attempt + 1))),
                    quality=int(85 * (0.9 ** (attempt + 1)))
                )
                base64_image = image_to_base64(compressed_image, format="JPEG")
                payload['messages'][0]['content'][1]['image_url']['url'] = (
                    f"data:image/jpeg;base64,{base64_image}"
                )
                time.sleep(2)
            else:
                print(f"  API调用失败: {e}")
                return None

        except Exception as e:
            print(f"  API调用异常: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                return None

    return None


def save_json(data: Dict, file_path: str) -> None:
    """
    保存JSON数据到文件

    Args:
        data: 要保存的字典数据
        file_path: 文件路径
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: str) -> Optional[Dict]:
    """
    从文件加载JSON数据

    Args:
        file_path: 文件路径

    Returns:
        字典数据，失败返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败: {e}")
        return None


def validate_bbox(bbox: List[int], page_width: int, page_height: int) -> bool:
    """
    验证边界框是否合法

    Args:
        bbox: 边界框 [x1, y1, x2, y2]
        page_width: 页面宽度
        page_height: 页面高度

    Returns:
        是否合法
    """
    if len(bbox) != 4:
        return False

    x1, y1, x2, y2 = bbox

    # 检查坐标顺序
    if x1 >= x2 or y1 >= y2:
        return False

    # 检查是否在页面范围内
    if x1 < 0 or y1 < 0 or x2 > page_width or y2 > page_height:
        return False

    return True


def calculate_iou(bbox1: List[int], bbox2: List[int]) -> float:
    """
    计算两个边界框的交并比（IoU）

    Args:
        bbox1: 边界框1 [x1, y1, x2, y2]
        bbox2: 边界框2 [x1, y1, x2, y2]

    Returns:
        IoU值（0-1）
    """
    x1_inter = max(bbox1[0], bbox2[0])
    y1_inter = max(bbox1[1], bbox2[1])
    x2_inter = min(bbox1[2], bbox2[2])
    y2_inter = min(bbox1[3], bbox2[3])

    # 计算交集面积
    if x2_inter <= x1_inter or y2_inter <= y1_inter:
        inter_area = 0
    else:
        inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)

    # 计算并集面积
    bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
    bbox2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
    union_area = bbox1_area + bbox2_area - inter_area

    if union_area == 0:
        return 0.0

    return inter_area / union_area


def check_overlap(elements: List[Dict], iou_threshold: float = 0.5) -> List[Tuple[int, int]]:
    """
    检查元素列表中的重叠框

    Args:
        elements: 元素列表（每个元素包含bbox字段）
        iou_threshold: IoU阈值（超过此值认为重叠）

    Returns:
        重叠元素对的索引列表 [(i, j), ...]
    """
    overlaps = []
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            bbox1 = elements[i]['bbox']
            bbox2 = elements[j]['bbox']
            iou = calculate_iou(bbox1, bbox2)
            if iou > iou_threshold:
                overlaps.append((i, j))
    return overlaps


if __name__ == "__main__":
    # 测试代码
    print("工具函数模块测试")
    print("=" * 50)

    # 测试PDF转图片
    test_pdf = "input_file/正文26春初中非常课课通数学8年级人教.pdf"
    if os.path.exists(test_pdf):
        print(f"\n测试PDF转图片: {test_pdf}")
        images = pdf_to_images(test_pdf, dpi=200, pages=[12])
        print(f"  成功转换 {len(images)} 页")
        for page_num, img in images:
            print(f"  第 {page_num} 页: {img.size[0]}x{img.size[1]} 像素")
