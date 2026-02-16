"""
图片处理器

统一的图片提取和处理接口，支持：
1. 从PDF提取图片（使用OpenCV检测）
2. 从DOCX提取图片（直接提取）
3. 图片清理和优化
"""

import io
import os
import logging
from typing import Dict, List, Tuple
from PIL import Image

# Optional OpenCV support
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available. PDF image extraction will use fallback method.")

# Optional python-docx support
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx not available. DOCX image extraction disabled.")


# Optional PyMuPDF support
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF not available. PDF rendering disabled.")


logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片提取和处理处理器"""

    def __init__(self, config: Dict):
        """
        初始化图片处理器

        Args:
            config: 配置字典，从config/default.yaml加载
        """
        self.config = config
        self.pdf_config = config.get('processing', {}).get('pdf', {})
        self.docx_config = config.get('processing', {}).get('docx', {})
        self.image_config = config.get('image_extraction', {})

        # OpenCV参数
        self.opencv_min_area = self.pdf_config.get('opencv_min_area', 0.02)
        self.opencv_padding = self.pdf_config.get('opencv_padding', 10)

        # DOCX图片参数
        self.image_max_size = self.docx_config.get('image_max_size', 1280)
        self.image_quality = self.docx_config.get('image_quality', 85)

    # ========================================
    # 公共方法
    # ========================================

    def extract_from_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        dpi: int = 200,
        max_pages: int = None,
        use_opencv: bool = True
    ) -> List[Dict]:
        """
        从PDF提取图片

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            dpi: 渲染DPI
            max_pages: 最大处理页数
            use_opencv: 是否使用OpenCV检测（如果False，则跳过图片提取）

        Returns:
            图片信息列表: [{
                'filename': str,
                'page': int,
                'bbox': tuple,  # (x, y, w, h)
                'path': str
            }, ...]
        """
        if not PYMUPDF_AVAILABLE:
            logger.error("❌ PyMuPDF未安装，无法处理PDF")
            return []

        if use_opencv and not OPENCV_AVAILABLE:
            logger.warning("⚠️  OpenCV未安装，将跳过图片提取")
            return []

        logger.info("=" * 60)
        logger.info("PDF图片提取")
        logger.info("=" * 60)

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
            if use_opencv and OPENCV_AVAILABLE:
                images_info = self._detect_with_opencv(page_image_path, page_num + 1)
            else:
                images_info = []

            # 裁剪并保存图片
            for idx, img_info in enumerate(images_info):
                bbox = img_info['bbox']
                filename = f'page_{page_num + 1:03d}_img_{idx + 1:02d}.png'
                output_path = os.path.join(images_dir, filename)

                if self._crop_image_from_page(page_image_path, bbox, output_path):
                    img_info['filename'] = filename
                    img_info['path'] = output_path
                    all_images.append(img_info)
                    logger.info(f"  ✓ 保存: {filename}")

            # 删除临时页面图片
            os.remove(page_image_path)

        pdf.close()

        logger.info(f"\n✅ 图片提取完成! 提取了 {len(all_images)} 个图片")
        return all_images

    def extract_from_docx(
        self,
        docx_path: str,
        images_dir: str
    ) -> Tuple[List[Dict], int]:
        """
        从DOCX提取图片

        Args:
            docx_path: DOCX文件路径
            images_dir: 图片输出目录

        Returns:
            (图片信息列表, 过滤数量)
            图片信息: [{
                'filename': str,
                'width': int,
                'height': int,
                'size': int
            }, ...]
        """
        if not DOCX_AVAILABLE:
            logger.error("❌ python-docx未安装，无法处理DOCX")
            return [], 0

        logger.info("从DOCX提取图片...")

        os.makedirs(images_dir, exist_ok=True)

        doc = Document(docx_path)
        images = []
        filtered_count = 0

        image_rel = doc.part._rels
        for r_id, rel in image_rel.items():
            if "image" in rel.target_ref:
                try:
                    image_data = rel.target_part.blob

                    # 检查图片尺寸
                    img = Image.open(io.BytesIO(image_data))
                    width, height = img.size

                    # 应用过滤条件
                    min_width = self.image_config.get('min_width', 50)
                    min_height = self.image_config.get('min_height', 50)

                    if width < min_width or height < min_height:
                        filtered_count += 1
                        continue

                    # 保存图片
                    image_filename = f"image{len(images)+1}.png"
                    image_path = os.path.join(images_dir, image_filename)

                    with open(image_path, 'wb') as f:
                        f.write(image_data)

                    images.append({
                        'filename': image_filename,
                        'width': width,
                        'height': height,
                        'size': len(image_data)
                    })

                except Exception as e:
                    logger.warning(f"提取图片失败: {e}")
                    continue

        logger.info(f"✓ 提取了 {len(images)} 张图片 (过滤了 {filtered_count} 张)")
        return images, filtered_count

    def optimize_image(
        self,
        image_path: str,
        max_size: int = None,
        quality: int = None
    ) -> str:
        """
        优化图片（压缩和调整尺寸）

        Args:
            image_path: 图片路径
            max_size: 最大尺寸（长边）
            quality: JPEG质量（1-100）

        Returns:
            优化后的图片路径（覆盖原文件）
        """
        if max_size is None:
            max_size = self.image_max_size
        if quality is None:
            quality = self.image_quality

        try:
            img = Image.open(image_path)

            # 调整尺寸（如果需要）
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # 转换模式（如果需要）
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            # 保存优化后的图片
            img.save(image_path, format='JPEG', quality=quality, optimize=True)

            logger.debug(f"优化图片: {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"优化图片失败 {image_path}: {e}")
            return image_path

    # ========================================
    # 私有方法
    # ========================================

    def _detect_with_opencv(self, page_image: str, page_num: int) -> List[Dict]:
        """
        使用OpenCV检测页面中的图片

        Args:
            page_image: 页面图片路径
            page_num: 页码

        Returns:
            检测到的图片信息列表
        """
        if not OPENCV_AVAILABLE:
            return []

        logger.info(f"  使用OpenCV检测图片区域...")

        # 读取图片
        img = cv2.imread(page_image)
        if img is None:
            logger.error(f"    ❌ 无法读取图片: {page_image}")
            return []

        height, width = img.shape[:2]
        logger.debug(f"    页面尺寸: {width}x{height}")

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
        min_area = width * height * self.opencv_min_area

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)

            # 扩展边界框
            x = max(0, x - self.opencv_padding)
            y = max(0, y - self.opencv_padding)
            w = min(width - x, w + 2 * self.opencv_padding)
            h = min(height - y, h + 2 * self.opencv_padding)

            images_info.append({
                'bbox': (x, y, w, h),
                'page': page_num
            })

        logger.debug(f"    检测到 {len(images_info)} 个图片区域")
        return images_info

    def _crop_image_from_page(
        self,
        page_image: str,
        bbox: Tuple[int, int, int, int],
        output_path: str
    ) -> bool:
        """
        从页面图片中裁剪图片

        Args:
            page_image: 页面图片路径
            bbox: 边界框 (x, y, w, h)
            output_path: 输出路径

        Returns:
            是否成功
        """
        try:
            img = Image.open(page_image)
            x, y, w, h = bbox

            # 裁剪图片
            cropped = img.crop((x, y, x + w, y + h))

            # 保存
            cropped.save(output_path, 'PNG')
            return True

        except Exception as e:
            logger.error(f"裁剪图片失败: {e}")
            return False

    def merge_overlapping_bboxes(
        self,
        bboxes: List[Tuple[int, int, int, int]],
        padding: int = 10
    ) -> List[Tuple[int, int, int, int]]:
        """
        合并重叠的边界框

        Args:
            bboxes: 边界框列表 [(x, y, w, h), ...]
            padding: 合并时的扩展像素

        Returns:
            合并后的边界框列表
        """
        if not bboxes:
            return []

        # 按x坐标排序
        sorted_boxes = sorted(bboxes, key=lambda b: b[0])

        merged = []
        current = sorted_boxes[0]

        for bbox in sorted_boxes[1:]:
            # 检查是否重叠或接近
            if (bbox[0] <= current[0] + current[2] + padding and
                bbox[1] <= current[1] + current[3] + padding):

                # 合并
                x = min(current[0], bbox[0])
                y = min(current[1], bbox[1])
                w = max(current[0] + current[2], bbox[0] + bbox[2]) - x
                h = max(current[1] + current[3], bbox[1] + bbox[3]) - y
                current = (x, y, w, h)
            else:
                merged.append(current)
                current = bbox

        merged.append(current)
        return merged
