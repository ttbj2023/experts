#!/usr/bin/env python3
"""
从扫描书籍PDF中提取插图
使用GLM-4.6V-Flash高精度识别图片位置并裁剪
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from process_pdf_with_glm46v_universal import GLM46VProcessor


class ImageExtractor:
    """从PDF中提取插图的工具"""

    def __init__(self, api_url: str = 'http://192.168.100.110:9999'):
        self.processor = GLM46VProcessor(api_url=api_url)
        self.extracted_images = []  # 记录所有提取的图片信息

    def clean_think_tags(self, text: str) -> str:
        """移除GLM的思考过程标签 </think>...
"""
        pattern = r'​*​*​*'
        cleaned = re.sub(pattern, '', text, flags=re.DOTALL)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    def detect_images_with_opencv(self, page_image: str) -> List[Dict]:
        """
        使用OpenCV检测页面中的图片（更可靠的方法）

        Args:
            page_image: 页面图片路径

        Returns:
            图片信息列表: [{"bbox": [x1, y1, x2, y2]}]
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            print('    ⚠️  需要安装 opencv-python: pip install opencv-python')
            return []

        print(f'    使用OpenCV检测图片区域...')

        # 读取图片
        img = cv2.imread(page_image)
        if img is None:
            print(f'    ❌ 无法读取图片: {page_image}')
            return []

        height, width = img.shape[:2]
        print(f'    页面尺寸: {width}x{height}')

        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 使用Canny边缘检测
        edges = cv2.Canny(gray, 50, 150)

        # 膨胀边缘，连接断裂的边缘
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)

        # 查找轮廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        images_info = []

        # 过滤掉太小的轮廓
        min_area = width * height * 0.02  # 至少占页面2%面积

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)

            # 扩展边界框（包含边缘）
            padding = 10
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(width, x + w + padding)
            y2 = min(height, y + h + padding)

            # 检查是否可能是图片（宽高比合理，面积足够大）
            bbox_area = (x2 - x1) * (y2 - y1)
            aspect_ratio = (x2 - x1) / (y2 - y1) if (y2 - y1) > 0 else 0

            # 过滤条件：面积至少占页面1%，宽高比在合理范围内
            if bbox_area > width * height * 0.01 and 0.2 < aspect_ratio < 5:
                images_info.append({
                    "bbox": [x1, y1, x2, y2],
                    "type": "图片",
                    "description": ""
                })

        # 合并重叠或相邻的bbox
        if len(images_info) > 1:
            images_info = self._merge_overlapping_bboxes(images_info)

        print(f'    ✓ 检测到 {len(images_info)} 个图片区域')
        return images_info

    def _merge_overlapping_bboxes(self, images_info: List[Dict]) -> List[Dict]:
        """
        合并重叠或相邻的边界框

        Args:
            images_info: 图片信息列表

        Returns:
            合并后的图片信息列表
        """
        if not images_info:
            return []

        # 按x坐标排序
        sorted_info = sorted(images_info, key=lambda x: x['bbox'][0])
        merged = [sorted_info[0]]

        for current in sorted_info[1:]:
            last = merged[-1]
            last_bbox = last['bbox']
            curr_bbox = current['bbox']

            # 检查是否重叠或相邻（距离小于50像素）
            if (curr_bbox[0] < last_bbox[2] + 50 and
                curr_bbox[1] < last_bbox[3] + 50):

                # 合并bbox
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

    def detect_images_in_page(
        self,
        page_image: str,
        page_num: int,
        use_opencv: bool = True
    ) -> List[Dict]:
        """
        检测页面中的图片

        Args:
            page_image: 页面图片路径
            page_num: 页码
            use_opencv: 是否使用OpenCV检测（默认True，更准确）

        Returns:
            图片信息列表: [{"bbox": [x1, y1, x2, y2], "type": "...", "description": "..."}]
        """
        print(f'  正在分析第 {page_num} 页的图片...')

        # 优先使用OpenCV方法
        if use_opencv:
            return self.detect_images_with_opencv(page_image)

        # 否则使用GLM方法（备用）
        # 压缩图片
        image_base64 = self.processor.compress_image(page_image, compression='medium')

        # 设计专门的图片检测prompt（简化版，因为bbox可能不准确）
        prompt = """你是一个专业的文档分析系统。请分析这个扫描页面，找出所有的图片、插图、图表、照片。

## 输出要求

请以JSON格式输出页面中所有图片的信息：

```json
[
  {
    "bbox": [x1, y1, x2, y2],
    "type": "图片类型",
    "description": "简要描述图片内容"
  }
]
```

## 坐标说明
- bbox格式: [x1, y1, x2, y2]
- (x1, y1): 图片左上角坐标
- (x2, y2): 图片右下角坐标
- 坐标范围: (0, 0) 在左上角，向右x增大，向下y增大
- 请使用页面实际像素尺寸估算坐标

## 注意事项
1. 如果没有图片，返回空数组: []
2. 只返回JSON，不要有其他内容"""

        # 调用GLM-4.6V-Flash
        response = self.processor.call_glm46v_api(
            image_base64,
            prompt,
            max_tokens=4096,
            retry_count=2
        )

        if 'error' in response:
            print(f'    ❌ API调用失败: {response["error"]}')
            return []

        # 提取响应内容
        content = response['choices'][0]['message']['content']
        content = self.clean_think_tags(content)

        # 解析JSON
        try:
            # 查找JSON代码块
            json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = content.strip()

            images_info = json.loads(json_str)

            if not isinstance(images_info, list):
                print(f'    ⚠️  返回格式错误，应为列表')
                return []

            print(f'    ✓ 检测到 {len(images_info)} 个图片')
            return images_info

        except json.JSONDecodeError as e:
            print(f'    ❌ JSON解析失败: {e}')
            print(f'    原始内容预览: {content[:200]}...')
            return []

    def crop_image_from_page(
        self,
        page_image_path: str,
        bbox: List[int],
        output_path: str
    ) -> bool:
        """
        从页面图片中裁剪出指定区域

        Args:
            page_image_path: 页面图片路径
            bbox: [x1, y1, x2, y2]
            output_path: 输出路径

        Returns:
            是否成功
        """
        try:
            from PIL import Image

            # 打开页面图片
            page_img = Image.open(page_image_path)
            width, height = page_img.size

            # 验证bbox
            x1, y1, x2, y2 = bbox
            if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
                print(f'    ⚠️  bbox超出页面范围: {bbox}, 页面尺寸: {width}x{height}')
                # 调整bbox
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
            print(f'    ❌ 裁剪失败: {e}')
            return False

    def extract_images_from_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        dpi: int = 200,
        max_pages: int = None
    ) -> Dict:
        """
        从PDF中提取所有图片

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            dpi: 渲染DPI
            max_pages: 最大处理页数（None表示全部）

        Returns:
            提取结果统计
        """
        print(f'\n{"="*60}')
        print(f'PDF图片提取工具')
        print(f'{"="*60}')
        print(f'输入文件: {pdf_path}')
        print(f'输出目录: {output_dir}')
        print(f'渲染DPI: {dpi}')
        print()

        # 打开PDF
        pdf = fitz.open(pdf_path)
        total_pages = len(pdf)

        if max_pages:
            total_pages = min(total_pages, max_pages)

        print(f'总页数: {len(pdf)} (处理前 {total_pages} 页)\n')

        # 创建输出目录
        images_dir = os.path.join(output_dir, 'extracted_images')
        os.makedirs(images_dir, exist_ok=True)

        # 处理每一页
        total_extracted = 0
        for page_num in range(total_pages):
            print(f'{"─"*60}')
            print(f'处理第 {page_num + 1}/{total_pages} 页')
            print(f'{"─"*60}')

            # 渲染页面为图片
            page = pdf[page_num]
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)

            page_image_path = os.path.join(output_dir, f'.temp_page_{page_num + 1}.png')
            pix.save(page_image_path)
            print(f'  ✓ 渲染页面: {pix.width}x{pix.height}')

            # 检测图片
            images_info = self.detect_images_in_page(page_image_path, page_num + 1)

            if not images_info:
                print(f'  ℹ️  该页无图片')
                # 删除临时页面图片
                os.remove(page_image_path)
                continue

            # 裁剪并保存每个图片
            for idx, img_info in enumerate(images_info):
                bbox = img_info.get('bbox')
                img_type = img_info.get('type', '未知')
                description = img_info.get('description', '')

                if not bbox or len(bbox) != 4:
                    print(f'    ⚠️  跳过无效bbox: {bbox}')
                    continue

                # 生成文件名
                filename = f'page_{page_num + 1:03d}_img_{idx + 1:02d}.png'
                output_path = os.path.join(images_dir, filename)

                # 裁剪保存
                if self.crop_image_from_page(page_image_path, bbox, output_path):
                    total_extracted += 1

                    # 记录信息
                    record = {
                        'page': page_num + 1,
                        'index': idx + 1,
                        'filename': filename,
                        'path': output_path,
                        'bbox': bbox,
                        'type': img_type,
                        'description': description
                    }
                    self.extracted_images.append(record)

                    print(f'    ✓ 保存: {filename} ({img_type})')

            # 删除临时页面图片
            os.remove(page_image_path)

        pdf.close()

        # 生成索引文件
        index_path = os.path.join(output_dir, 'image_index.json')
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump({
                'source_pdf': pdf_path,
                'total_images': total_extracted,
                'images': self.extracted_images
            }, f, ensure_ascii=False, indent=2)

        print(f'\n{"="*60}')
        print(f'✅ 提取完成！')
        print(f'{"="*60}')
        print(f'总计提取: {total_extracted} 个图片')
        print(f'保存位置: {images_dir}')
        print(f'索引文件: {index_path}')
        print(f'{"="*60}\n')

        return {
            'total_images': total_extracted,
            'images_dir': images_dir,
            'index_path': index_path
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='从PDF中提取插图')
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('-o', '--output', default='./extracted_images_output', help='输出目录')
    parser.add_argument('-d', '--dpi', type=int, default=200, help='渲染DPI')
    parser.add_argument('-n', '--max-pages', type=int, help='最大处理页数')

    args = parser.parse_args()

    # 检查文件
    if not os.path.exists(args.pdf_path):
        print(f'❌ 文件不存在: {args.pdf_path}')
        return 1

    # 创建提取器
    extractor = ImageExtractor()

    # 提取图片
    result = extractor.extract_images_from_pdf(
        args.pdf_path,
        args.output,
        dpi=args.dpi,
        max_pages=args.max_pages
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
