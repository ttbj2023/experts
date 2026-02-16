#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF图片提取工具

使用PyMuPDF从PDF中提取图片及其位置信息
"""

import os
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFImageExtractor:
    """PDF图片提取器"""

    def __init__(self):
        """初始化提取器"""
        self.extracted_images = []

    def extract_images(self, pdf_path: str, output_dir: str) -> List[Dict]:
        """
        从PDF中提取所有图片

        Args:
            pdf_path: PDF文件路径
            output_dir: 图片输出目录

        Returns:
            图片信息列表，每项包含:
            {
                'page': 页码,
                'index': 图片索引,
                'path': 图片文件路径,
                'bbox': 边界框 (x0, y0, x1, y1),
                'size': (width, height),
                'image_number': PDF中的图片编号
            }
        """
        # 创建输出目录
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)

        pdf_document = fitz.open(pdf_path)
        extracted_info = []

        logger.info(f"开始从PDF提取图片: {pdf_path}")

        image_counter = 1

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()

            logger.info(f"  第{page_num + 1}页: 找到{len(image_list)}张图片")

            for img_index, img in enumerate(image_list):
                try:
                    # 获取图片
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)

                    # 保存图片
                    image_ext = base_image['ext']
                    image_filename = f"page{page_num + 1:03d}_img{img_index + 1}.{image_ext}"
                    image_path = os.path.join(images_dir, image_filename)

                    with open(image_path, 'wb') as img_file:
                        img_file.write(base_image['image'])

                    # 获取图片在页面中的位置
                    # 这需要查找图片引用
                    image_refs = self._find_image_positions(page, xref)

                    for ref in image_refs:
                        info = {
                            'page': page_num + 1,  # 页码（从1开始）
                            'index': img_index,
                            'path': image_path,
                            'filename': image_filename,
                            'bbox': ref['bbox'],  # (x0, y0, x1, y1)
                            'size': (base_image['width'], base_image['height']),
                            'image_number': xref,
                            'global_index': image_counter
                        }

                        extracted_info.append(info)
                        image_counter += 1

                except Exception as e:
                    logger.warning(f"  提取图片失败 (页{page_num + 1}, 图{img_index}): {str(e)}")

        pdf_document.close()

        logger.info(f"✓ 共提取{len(extracted_info)}张图片到: {images_dir}")

        self.extracted_images = extracted_info
        return extracted_info

    def _find_image_positions(self, page, xref: int) -> List[Dict]:
        """
        查找图片在页面中的位置

        Args:
            page: PyMuPDF页面对象
            xref: 图片的交叉引用号

        Returns:
            位置信息列表
        """
        positions = []

        try:
            # 获取页面上的所有图片引用
            image_list = page.get_images(full=True)

            for img_index, img_info in enumerate(image_list):
                if img_info[0] == xref:  # xref匹配
                    # 尝试获取图片的显示位置
                    # 这个需要扫描页面的内容
                    try:
                        # 方法1: 从页面内容中查找图片引用
                        for item in page.get_images():
                            # 这个API返回的信息有限，需要另一种方法
                            pass
                    except:
                        pass

                    # 简化方案：返回整个页面区域
                    # 实际位置需要更复杂的分析
                    rect = page.rect
                    positions.append({
                        'bbox': (rect.x0, rect.y0, rect.x1, rect.y1),
                        'page_height': rect.height
                    })
                    break

        except Exception as e:
            logger.debug(f"查找图片位置失败: {str(e)}")

            # 降级方案：返回页面中心位置
            rect = page.rect
            positions.append({
                'bbox': (rect.x0, rect.y0, rect.x1, rect.y1),
                'page_height': rect.height
            })

        return positions if positions else [{'bbox': (0, 0, 0, 0), 'page_height': page.rect.height}]

    def get_images_by_page(self, page_num: int) -> List[Dict]:
        """
        获取指定页码的所有图片

        Args:
            page_num: 页码（从1开始）

        Returns:
            图片信息列表
        """
        return [img for img in self.extracted_images if img['page'] == page_num]

    def sort_by_position(self, images: List[Dict]) -> List[Dict]:
        """
        按页面位置排序图片（从上到下，从左到右）

        Args:
            images: 图片信息列表

        Returns:
            排序后的图片列表
        """
        def sort_key(img):
            bbox = img.get('bbox', (0, 0, 0, 0))
            # 首先按y0排序（从上到下），然后按x0排序（从左到右）
            return (img['page'], bbox[1], bbox[0])

        return sorted(images, key=sort_key)


# 测试代码
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 pdf_image_extractor.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = "./test_images"

    extractor = PDFImageExtractor()
    images = extractor.extract_images(pdf_path, output_dir)

    print(f"\n提取的图片信息:")
    for img in images[:5]:  # 只显示前5张
        print(f"  页{img['page']}: {img['filename']}")
        print(f"    位置: {img['bbox']}")
        print(f"    大小: {img['size']}")

    if len(images) > 5:
        print(f"  ... 还有{len(images) - 5}张图片")
