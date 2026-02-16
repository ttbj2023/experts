"""
统一转换器

智能识别文档类型并选择最优处理流程
"""

import os
import logging
from typing import Dict, Tuple
from .base import BaseConverter
from .pdf_converter import PDFConverter
from .docx_converter import DOCXConverter
from ..core.document_detector import DocumentDetector
from ..core.text_extractor import TextExtractor
from ..core.deepseek_client import DeepSeekClient


logger = logging.getLogger(__name__)


class UnifiedConverter(BaseConverter):
    """
    统一文档转换器

    智能检测文档类型并选择最优处理流程：

    PDF文档：
    - 数字版PDF → 直接提取文本 + DeepSeek格式化（快速）
    - 扫描版PDF → 完整OCR流程（PDFConverter）

    DOCX文档：
    - 简单DOCX → 直接提取文本 + DeepSeek格式化（快速）
    - 复杂DOCX → LibreOffice + OCR流程（DOCXConverter）
    """

    def __init__(self, config_path: str = None):
        """初始化统一转换器"""
        super().__init__(config_path)

        # 初始化检测器和提取器
        self.detector = DocumentDetector(self.config)
        self.extractor = TextExtractor(self.config)
        self.deepseek_client = DeepSeekClient(self.config)

        # 初始化专用转换器（用于复杂文档）
        self.pdf_converter = PDFConverter(config_path)
        self.docx_converter = DOCXConverter(config_path)

        # 获取检测配置
        self.detection_config = self.config.get('detection', {})
        self.fallback_on_error = self.detection_config.get('fallback_on_error', True)

    def convert(
        self,
        input_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """
        智能转换文档（自动选择最优流程）

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            **kwargs: 额外参数（传递给底层转换器）

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self._start_timer()

        self.logger.info("\n" + "=" * 70)
        self.logger.info("🤖 智能文档转换器")
        self.logger.info("=" * 70)
        self.logger.info(f"输入文件: {input_path}")
        self.logger.info(f"输出目录: {output_dir}")

        try:
            # ========== 阶段1: 检测文档类型 ==========
            self.logger.info("\n" + "-" * 70)
            self.logger.info("🔍 阶段1: 检测文档类型...")
            self.logger.info("-" * 70)

            file_format, subtype = self.detector.detect_document_type(input_path)

            self.logger.info(f"✅ 检测结果:")
            self.logger.info(f"   - 文件格式: {file_format.upper()}")
            self.logger.info(f"   - 子类型: {subtype}")

            # ========== 阶段2: 选择处理流程 ==========
            self.logger.info("\n" + "-" * 70)
            self.logger.info("⚙️  阶段2: 选择处理流程...")
            self.logger.info("-" * 70)

            # PDF文档
            if file_format == 'pdf':
                if subtype == 'digital':
                    self.logger.info("✅ 流程: 数字版PDF快速提取")
                    return self._process_digital_pdf(input_path, output_dir, **kwargs)
                else:  # scanned
                    self.logger.info("✅ 流程: 扫描版PDF完整OCR")
                    return self._delegate_to_pdf_converter(input_path, output_dir, **kwargs)

            # DOCX文档
            elif file_format == 'docx':
                if subtype == 'simple':
                    self.logger.info("✅ 流程: 简单DOCX快速提取")
                    return self._process_simple_docx(input_path, output_dir, **kwargs)
                else:  # complex
                    self.logger.info("✅ 流程: 复杂DOCX完整处理")
                    return self._delegate_to_docx_converter(input_path, output_dir, **kwargs)

            else:
                raise ValueError(f"不支持的文件格式: {file_format}")

        except Exception as e:
            self.logger.error(f"❌ 转换失败: {e}")

            # 回退机制：如果配置了回退，尝试使用完整流程
            if self.fallback_on_error:
                self.logger.info("\n" + "-" * 70)
                self.logger.info("🔄 触发回退机制，使用完整流程...")
                self.logger.info("-" * 70)

                ext = os.path.splitext(input_path)[1].lower()
                if ext == '.pdf':
                    return self._delegate_to_pdf_converter(input_path, output_dir, **kwargs)
                elif ext in ['.docx', '.doc']:
                    return self._delegate_to_docx_converter(input_path, output_dir, **kwargs)

            raise

    # ========================================
    # 快速处理流程（新增）
    # ========================================

    def _process_digital_pdf(
        self,
        input_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """
        处理数字版PDF（快速流程）

        流程：
        1. PyMuPDF直接提取文本
        2. 提取嵌入图片
        3. DeepSeek格式化为Markdown

        Args:
            input_path: PDF文件路径
            output_dir: 输出目录
            **kwargs: 额外参数

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📄 数字版PDF快速处理")
        self.logger.info("=" * 70)

        try:
            # ========== Step 1: 提取文本和图片 ==========
            self.logger.info("\n[1/3] 提取文本和图片...")

            raw_text, image_paths = self.extractor.extract_from_digital_pdf(input_path)

            self.logger.info(f"✅ 提取完成:")
            self.logger.info(f"   - 文本长度: {len(raw_text)} 字符")
            self.logger.info(f"   - 图片数量: {len(image_paths)}")

            # 保存原始文本（用于调试）
            if self.config.get('output', {}).get('save_intermediate', True):
                raw_text_file = os.path.join(output_dir, 'stage1_raw_text.txt')
                os.makedirs(output_dir, exist_ok=True)
                with open(raw_text_file, 'w', encoding='utf-8') as f:
                    f.write(raw_text)
                self.logger.info(f"💾 保存原始文本: {raw_text_file}")

            # ========== Step 2: DeepSeek格式化 ==========
            self.logger.info("\n[2/3] DeepSeek格式化为Markdown...")

            formatted_markdown = self.deepseek_client.format_markdown(raw_text)

            self.logger.info(f"✅ 格式化完成: {len(formatted_markdown)} 字符")

            # 保存格式化结果
            if self.config.get('output', {}).get('save_intermediate', True):
                formatted_file = os.path.join(output_dir, 'stage2_formatted.md')
                os.makedirs(output_dir, exist_ok=True)
                with open(formatted_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_markdown)
                self.logger.info(f"💾 保存格式化结果: {formatted_file}")

            # ========== Step 3: 替换图片路径 ==========
            self.logger.info("\n[3/3] 处理图片路径...")

            final_markdown = self._replace_image_paths(
                formatted_markdown,
                image_paths,
                output_dir
            )

            # 保存最终结果
            os.makedirs(output_dir, exist_ok=True)
            output_file = self._get_output_filename(input_path, output_dir)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            # 更新统计信息
            self.stats['input_file'] = input_path
            self.stats['output_file'] = output_file
            self.stats['total_images'] = len(image_paths)
            self.stats['processing_method'] = 'fast_digital_pdf'
            self.stats['stages_completed'] = [
                'Step 1: 文本提取',
                'Step 2: DeepSeek格式化',
                'Step 3: 图片处理'
            ]

            # 保存元数据
            self._save_metadata(output_dir, self.stats)
            self._stop_timer()

            self.logger.info("\n" + "=" * 70)
            self.logger.info("✅ 数字版PDF处理完成")
            self.logger.info("=" * 70)
            self.logger.info(f"输出文件: {output_file}")
            self.logger.info(f"处理时间: {self.stats['processing_time']:.2f}秒")

            return True, output_file, self.stats

        except Exception as e:
            self.logger.error(f"数字版PDF处理失败: {e}")
            # 如果快速流程失败，回退到完整OCR流程
            if self.fallback_on_error:
                self.logger.info("🔄 回退到完整OCR流程...")
                return self._delegate_to_pdf_converter(input_path, output_dir, **kwargs)
            raise

    def _process_simple_docx(
        self,
        input_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """
        处理简单DOCX（快速流程）

        流程：
        1. python-docx直接提取文本
        2. DeepSeek格式化为Markdown

        Args:
            input_path: DOCX文件路径
            output_dir: 输出目录
            **kwargs: 额外参数

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📝 简单DOCX快速处理")
        self.logger.info("=" * 70)

        try:
            # ========== Step 1: 提取文本和图片 ==========
            self.logger.info("\n[1/3] 提取文本和图片...")

            raw_text, image_paths = self.extractor.extract_from_simple_docx(input_path)

            self.logger.info(f"✅ 提取完成:")
            self.logger.info(f"   - 文本长度: {len(raw_text)} 字符")
            self.logger.info(f"   - 图片数量: {len(image_paths)}")

            # 保存原始文本
            if self.config.get('output', {}).get('save_intermediate', True):
                raw_text_file = os.path.join(output_dir, 'stage1_raw_text.txt')
                os.makedirs(output_dir, exist_ok=True)
                with open(raw_text_file, 'w', encoding='utf-8') as f:
                    f.write(raw_text)
                self.logger.info(f"💾 保存原始文本: {raw_text_file}")

            # ========== Step 2: DeepSeek格式化 ==========
            self.logger.info("\n[2/3] DeepSeek格式化为Markdown...")

            formatted_markdown = self.deepseek_client.format_markdown(raw_text)

            self.logger.info(f"✅ 格式化完成: {len(formatted_markdown)} 字符")

            # 保存格式化结果
            if self.config.get('output', {}).get('save_intermediate', True):
                formatted_file = os.path.join(output_dir, 'stage2_formatted.md')
                os.makedirs(output_dir, exist_ok=True)
                with open(formatted_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_markdown)
                self.logger.info(f"💾 保存格式化结果: {formatted_file}")

            # ========== Step 3: 替换图片路径 ==========
            self.logger.info("\n[3/3] 处理图片路径...")

            final_markdown = self._replace_image_paths(
                formatted_markdown,
                image_paths,
                output_dir
            )

            # 保存最终结果
            os.makedirs(output_dir, exist_ok=True)
            output_file = self._get_output_filename(input_path, output_dir)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            # 更新统计信息
            self.stats['input_file'] = input_path
            self.stats['output_file'] = output_file
            self.stats['total_images'] = len(image_paths)
            self.stats['processing_method'] = 'fast_simple_docx'
            self.stats['stages_completed'] = [
                'Step 1: 文本提取',
                'Step 2: DeepSeek格式化',
                'Step 3: 图片处理'
            ]

            # 保存元数据
            self._save_metadata(output_dir, self.stats)
            self._stop_timer()

            self.logger.info("\n" + "=" * 70)
            self.logger.info("✅ 简单DOCX处理完成")
            self.logger.info("=" * 70)
            self.logger.info(f"输出文件: {output_file}")
            self.logger.info(f"处理时间: {self.stats['processing_time']:.2f}秒")

            return True, output_file, self.stats

        except Exception as e:
            self.logger.error(f"简单DOCX处理失败: {e}")
            # 如果快速流程失败，回退到完整流程
            if self.fallback_on_error:
                self.logger.info("🔄 回退到完整处理流程...")
                return self._delegate_to_docx_converter(input_path, output_dir, **kwargs)
            raise

    # ========================================
    # 委托处理（复用现有转换器）
    # ========================================

    def _delegate_to_pdf_converter(
        self,
        input_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """委托给PDF转换器处理"""
        self.logger.info("📋 使用PDF完整OCR流程...")
        return self.pdf_converter.convert(input_path, output_dir, **kwargs)

    def _delegate_to_docx_converter(
        self,
        input_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """委托给DOCX转换器处理"""
        self.logger.info("📋 使用DOCX完整处理流程...")
        return self.docx_converter.convert(input_path, output_dir, **kwargs)

    # ========================================
    # 工具方法
    # ========================================

    def _replace_image_paths(
        self,
        markdown: str,
        image_paths: list,
        output_dir: str
    ) -> str:
        """
        替换或添加图片引用

        Args:
            markdown: Markdown文本
            image_paths: 图片路径列表
            output_dir: 输出目录

        Returns:
            更新后的Markdown
        """
        if not image_paths:
            return markdown

        # 简单处理：在文件末尾添加图片列表
        # TODO: 更智能的图片插入逻辑（基于上下文）
        base_name = os.path.basename(output_dir)

        image_section = "\n\n## 文档图片\n\n"
        for i, img_path in enumerate(image_paths, 1):
            # 使用相对路径
            rel_path = os.path.relpath(img_path, output_dir)
            image_section += f"![图片 {i}]({rel_path})\n\n"

        return markdown + image_section

    def _start_timer(self):
        """开始计时"""
        import time
        self.stats['start_time'] = time.time()

    def _stop_timer(self):
        """停止计时"""
        import time
        if self.stats['start_time']:
            self.stats['end_time'] = time.time()
            self.stats['processing_time'] = self.stats['end_time'] - self.stats['start_time']
