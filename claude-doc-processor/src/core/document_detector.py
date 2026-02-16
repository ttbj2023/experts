"""
文档类型检测器

快速检测文档类型和复杂度，用于选择最优处理流程
"""

import os
import fitz  # PyMuPDF
import logging
from typing import Dict, Tuple, Optional
from docx import Document as DocxDocument


logger = logging.getLogger(__name__)


class DocumentDetector:
    """文档类型检测器"""

    def __init__(self, config: Dict = None):
        """
        初始化检测器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.detection_config = self.config.get('detection', {})

    # ========================================
    # PDF检测
    # ========================================

    def detect_pdf_type(self, pdf_path: str) -> str:
        """
        检测PDF类型：数字版 vs 扫描版

        检测逻辑：
        1. 使用PyMuPDF尝试提取文本
        2. 如果文本数量超过阈值 → 数字版（可直接提取）
        3. 如果文本数量很少 → 扫描版（需要OCR）

        Args:
            pdf_path: PDF文件路径

        Returns:
            "digital" 或 "scanned"
        """
        # 获取检测配置
        text_threshold = self.detection_config.get('pdf', {}).get('text_threshold', 1000)
        min_text_ratio = self.detection_config.get('pdf', {}).get('min_text_ratio', 0.1)

        try:
            doc = fitz.open(pdf_path)

            total_text_length = 0
            total_page_area = 0

            for page in doc:
                # 提取文本
                text = page.get_text()
                total_text_length += len(text)

                # 计算页面面积（用于估算预期文本量）
                page_rect = page.rect
                total_page_area += (page_rect.width * page_rect.height)

            doc.close()

            # 判断文本数量是否足够
            if total_text_length >= text_threshold:
                logger.info(f"PDF检测为数字版: 文本数量 {total_text_length} >= 阈值 {text_threshold}")
                return "digital"

            # 计算文本密度（字符/像素）
            text_density = total_text_length / total_page_area if total_page_area > 0 else 0

            if text_density >= min_text_ratio:
                logger.info(f"PDF检测为数字版: 文本密度 {text_density:.4f} >= 阈值 {min_text_ratio}")
                return "digital"

            logger.info(f"PDF检测为扫描版: 文本数量 {total_text_length} < 阈值 {text_threshold}")
            return "scanned"

        except Exception as e:
            logger.error(f"PDF类型检测失败: {e}")
            # 检测失败时，保守判断为扫描版（走完整流程）
            return "scanned"

    def analyze_pdf_structure(self, pdf_path: str) -> Dict:
        """
        分析PDF结构（用于更精确判断）

        Args:
            pdf_path: PDF文件路径

        Returns:
            结构信息字典
        """
        try:
            doc = fitz.open(pdf_path)

            info = {
                'page_count': doc.page_count,
                'has_images': False,
                'has_tables': False,
                'text_quality': 'unknown',
                'avg_text_per_page': 0
            }

            total_text = 0

            for page in doc:
                # 检查是否有图片
                image_list = page.get_images()
                if image_list:
                    info['has_images'] = True

                # 提取文本
                text = page.get_text()
                total_text += len(text)

                # 简单检测表格（通过文本特征）
                if '|' in text or '\t' in text:
                    info['has_tables'] = True

            info['avg_text_per_page'] = total_text / info['page_count'] if info['page_count'] > 0 else 0

            # 判断文本质量
            if info['avg_text_per_page'] > 500:
                info['text_quality'] = 'good'
            elif info['avg_text_per_page'] > 100:
                info['text_quality'] = 'medium'
            else:
                info['text_quality'] = 'poor'

            doc.close()

            return info

        except Exception as e:
            logger.error(f"PDF结构分析失败: {e}")
            return {}

    # ========================================
    # DOCX检测
    # ========================================

    def detect_docx_complexity(self, docx_path: str) -> str:
        """
        检测DOCX复杂度：简单 vs 复杂

        检测逻辑：
        1. 检查图片数量
        2. 检查复杂元素（公式、图表等）
        3. 如果无图片且无复杂元素 → 简单文档
        4. 否则 → 复杂文档

        Args:
            docx_path: DOCX文件路径

        Returns:
            "simple" 或 "complex"
        """
        # 获取检测配置
        max_images = self.detection_config.get('docx', {}).get('max_images', 0)
        complex_elements = self.detection_config.get('docx', {}).get('complex_elements', [])

        try:
            doc = DocxDocument(docx_path)

            # 统计图片数量
            image_count = 0
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    image_count += 1

            # 检测复杂元素
            has_complex_elements = False

            # 检查段落中的复杂元素
            for para in doc.paragraphs:
                # 检测公式（通过XML）
                if 'omath' in para._element.xml:
                    has_complex_elements = True
                    break

                # 检测SmartArt
                if 'smartArt' in para._element.xml.lower():
                    has_complex_elements = True
                    break

            # 检查表格中的复杂元素
            for table in doc.tables:
                if 'omath' in table._element.xml:
                    has_complex_elements = True
                    break

            # 判断
            if image_count <= max_images and not has_complex_elements:
                logger.info(f"DOCX检测为简单文档: 图片数={image_count}, 复杂元素=False")
                return "simple"
            else:
                logger.info(f"DOCX检测为复杂文档: 图片数={image_count}, 复杂元素={has_complex_elements}")
                return "complex"

        except Exception as e:
            logger.error(f"DOCX复杂度检测失败: {e}")
            # 检测失败时，保守判断为复杂文档（走完整流程）
            return "complex"

    def analyze_docx_structure(self, docx_path: str) -> Dict:
        """
        分析DOCX结构

        Args:
            docx_path: DOCX文件路径

        Returns:
            结构信息字典
        """
        try:
            doc = DocxDocument(docx_path)

            info = {
                'paragraph_count': len(doc.paragraphs),
                'table_count': len(doc.tables),
                'image_count': 0,
                'has_equations': False,
                'has_smartart': False,
                'has_complex_formatting': False
            }

            # 统计图片
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    info['image_count'] += 1

            # 检测复杂元素
            for para in doc.paragraphs:
                xml = para._element.xml
                if 'omath' in xml:
                    info['has_equations'] = True
                if 'smartArt' in xml.lower():
                    info['has_smartart'] = True

            return info

        except Exception as e:
            logger.error(f"DOCX结构分析失败: {e}")
            return {}

    # ========================================
    # 统一检测接口
    # ========================================

    def detect_document_type(self, file_path: str) -> Tuple[str, str]:
        """
        统一检测文档类型和子类型

        Args:
            file_path: 文档文件路径

        Returns:
            (文件格式, 子类型)
            文件格式: "pdf", "docx", "doc"
            子类型:
                - PDF: "digital" 或 "scanned"
                - DOCX: "simple" 或 "complex"
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()

        # PDF文件
        if ext == '.pdf':
            subtype = self.detect_pdf_type(file_path)
            return ('pdf', subtype)

        # DOCX文件
        elif ext in ['.docx', '.doc']:
            subtype = self.detect_docx_complexity(file_path)
            return ('docx', subtype)

        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    # ========================================
    # 工具方法
    # ========================================

    def get_file_extension(self, file_path: str) -> str:
        """获取文件扩展名（小写）"""
        return os.path.splitext(file_path)[1].lower()

    def is_supported_format(self, file_path: str) -> bool:
        """检查是否为支持的文件格式"""
        ext = self.get_file_extension(file_path)
        return ext in ['.pdf', '.docx', '.doc']
