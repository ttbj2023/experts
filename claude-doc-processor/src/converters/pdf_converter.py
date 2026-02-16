"""
PDF转换器

将PDF文档转换为Markdown，支持：
- GLM-4.6V-Flash OCR识别
- OpenCV图片提取
- DeepSeek语义匹配和排版优化
"""

import os
from typing import Dict, List, Tuple
import fitz  # PyMuPDF

from .base import BaseConverter
from ..core.glm_client import GLMClient
from ..core.deepseek_client import DeepSeekClient
from ..core.image_processor import ImageProcessor
from ..core.ocr_engine import OCREngine


class PDFConverter(BaseConverter):
    """
    PDF转Markdown转换器

    使用5阶段架构：
    - Stage 1: GLM OCR + 占位符
    - Stage 1.5: DeepSeek排版优化（可选）
    - Stage 2: OpenCV图片提取
    - Stage 3: GLM图片描述
    - Stage 4: DeepSeek语义匹配
    - Stage 5: 占位符替换
    """

    def __init__(self, config_path: str = None):
        """初始化PDF转换器"""
        super().__init__(config_path)

        # 初始化核心组件
        self.glm_client = GLMClient(self.config)
        self.deepseek_client = DeepSeekClient(self.config)
        self.image_processor = ImageProcessor(self.config)
        self.ocr_engine = OCREngine(self.config)

        # PDF处理配置
        self.pdf_config = self.config.get('processing', {}).get('pdf', {})
        self.dpi = self.pdf_config.get('dpi', 200)
        self.enable_formatting = self.pdf_config.get('enable_formatting', False)

    def convert(
        self,
        input_path: str,
        output_dir: str,
        max_pages: int = None,
        format_with_deepseek: bool = None
    ) -> Tuple[bool, str, Dict]:
        """
        执行PDF到Markdown的完整转换流程

        Args:
            input_path: PDF文件路径
            output_dir: 输出目录
            max_pages: 最大处理页数（None表示全部）
            format_with_deepseek: 是否启用DeepSeek排版优化

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self._start_timer()

        # 验证输入
        if not self._validate_input_file(input_path, ['.pdf']):
            return False, '', self.stats

        # 创建输出目录
        if not self._create_output_dir(output_dir):
            return False, '', self.stats

        # 更新配置
        if max_pages is None:
            max_pages = self.pdf_config.get('max_pages')
        if format_with_deepseek is None:
            format_with_deepseek = self.enable_formatting

        self.logger.info("\n" + "=" * 70)
        self.logger.info("PDF → Markdown 转换流程")
        self.logger.info("=" * 70)
        self.logger.info(f"输入: {input_path}")
        self.logger.info(f"输出: {output_dir}")
        self.logger.info(f"页数限制: {max_pages or '全部'}")
        self.logger.info(f"排版优化: {'启用' if format_with_deepseek else '禁用'}")

        try:
            # ========== Stage 1: OCR + 占位符 ==========
            markdown, placeholders = self._stage1_ocr_with_placeholders(
                input_path, max_pages
            )
            self.stats['stages_completed'].append('Stage 1: OCR + 占位符')

            # ========== Stage 1.5: DeepSeek排版优化（可选） ==========
            if format_with_deepseek:
                markdown = self._format_markdown_with_deepseek(markdown)
                self.stats['stages_completed'].append('Stage 1.5: DeepSeek排版优化')

            # 保存中间结果
            md_with_placeholders = os.path.join(output_dir, 'markdown_with_placeholders.md')
            with open(md_with_placeholders, 'w', encoding='utf-8') as f:
                f.write(markdown)
            self.logger.info(f"💾 保存: {md_with_placeholders}")

            # ========== 性能优化：如果没有图片占位符，跳过Stage 2-5 ==========
            if not placeholders:
                self.logger.info("\n" + "=" * 60)
                self.logger.info("⚡ 性能优化：未检测到图片占位符")
                self.logger.info("=" * 60)
                final_markdown = markdown
            else:
                # ========== Stage 2: 提取图片 ==========
                images = self._stage2_extract_images(input_path, output_dir, max_pages)
                self.stats['total_images'] = len(images)
                self.stats['stages_completed'].append('Stage 2: 提取图片')

                # ========== Stage 3: GLM图片描述 ==========
                image_descriptions = self._stage3_describe_images(images)
                self.stats['stages_completed'].append('Stage 3: GLM图片描述')

                # ========== Stage 4: DeepSeek语义匹配 ==========
                mapping = self._stage4_match_placeholders(markdown, placeholders, image_descriptions)
                self.stats['matched_images'] = len(mapping)
                self.stats['stages_completed'].append('Stage 4: DeepSeek语义匹配')

                # ========== Stage 5: 替换占位符 ==========
                final_markdown = self._stage5_replace_placeholders(markdown, placeholders, mapping, output_dir)
                self.stats['stages_completed'].append('Stage 5: 替换占位符')

            # 保存最终结果
            output_file = self._get_output_filename(input_path, output_dir)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            self.stats['input_file'] = input_path
            self.stats['output_file'] = output_file

            # 保存元数据和统计
            self._save_metadata(output_dir, self.stats)
            self._stop_timer()

            # 输出统计信息
            self._log_stats(self.stats)

            return True, output_file, self.stats

        except Exception as e:
            self.logger.error(f"❌ 转换失败: {e}")
            self._stop_timer()
            self.stats['error'] = str(e)
            return False, '', self.stats

    # ========================================
    # Stage 实现
    # ========================================

    def _stage1_ocr_with_placeholders(
        self,
        pdf_path: str,
        max_pages: int = None
    ) -> Tuple[str, List[Dict]]:
        """Stage 1: 使用GLM-4.6V-Flash进行OCR并生成图片占位符"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 1: GLM-4.6V-Flash OCR + 图片占位符")
        self.logger.info("=" * 60)

        pdf = fitz.open(pdf_path)
        total_pages = len(pdf)

        if max_pages:
            total_pages = min(total_pages, max_pages)

        self.logger.info(f"PDF文件: {pdf_path}")
        self.logger.info(f"总页数: {len(pdf)} (处理前 {total_pages} 页)")

        all_markdown = []
        all_placeholders = []
        placeholder_index = 0

        for page_num in range(total_pages):
            self.logger.info(f"\n处理第 {page_num + 1}/{total_pages} 页...")

            # 渲染页面
            page = pdf[page_num]
            mat = fitz.Matrix(self.dpi/72, self.dpi/72)
            pix = page.get_pixmap(matrix=mat)

            temp_image = f'/tmp/ocr_page_{page_num + 1}.png'
            pix.save(temp_image)

            # 调用GLM-4.6V-Flash OCR
            markdown = self.glm_client.ocr_page(temp_image)

            # 提取占位符
            page_placeholders = self.ocr_engine.extract_placeholders(
                markdown,
                page_num,
                placeholder_index
            )
            all_placeholders.extend(page_placeholders)
            placeholder_index += len(page_placeholders)

            self.logger.info(f"  ✓ OCR完成，提取到 {len(page_placeholders)} 个图片占位符")

            all_markdown.append(markdown)

            # 删除临时图片
            os.remove(temp_image)

        pdf.close()

        # 合并所有页面的Markdown
        final_markdown = ''.join(all_markdown)

        self.logger.info(f"\n✅ Stage 1 完成!")
        self.logger.info(f"  总共识别: {len(all_markdown)} 页")
        self.logger.info(f"  图片占位符: {len(all_placeholders)} 个")

        return final_markdown, all_placeholders

    def _format_markdown_with_deepseek(self, markdown: str) -> str:
        """使用DeepSeek-chat进行Markdown排版优化"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 1.5: DeepSeek排版优化")
        self.logger.info("=" * 60)
        self.logger.info(f"输入字符数: {len(markdown):,}")

        # 从config加载提示词模板
        prompt_template = self.config.get('prompts', {}).get('markdown_formatting')

        formatted_markdown = self.deepseek_client.format_markdown(markdown, prompt_template)

        self.logger.info(f"输出字符数: {len(formatted_markdown):,}")
        self.logger.info("✅ 排版优化完成")

        return formatted_markdown

    def _stage2_extract_images(
        self,
        pdf_path: str,
        output_dir: str,
        max_pages: int = None
    ) -> List[Dict]:
        """Stage 2: 使用OpenCV提取所有图片"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 2: OpenCV 精确图片提取")
        self.logger.info("=" * 60)

        images = self.image_processor.extract_from_pdf(
            pdf_path,
            output_dir,
            self.dpi,
            max_pages,
            use_opencv=True
        )

        return images

    def _stage3_describe_images(self, images: List[Dict]) -> List[Dict]:
        """Stage 3: 使用GLM-4V描述所有提取的图片"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 3: GLM-4V 图片描述")
        self.logger.info("=" * 60)

        image_descriptions = []

        for idx, img_info in enumerate(images, 1):
            filename = img_info['filename']
            image_path = img_info['path']

            self.logger.info(f"[{idx}/{len(images)}] 描述 {filename}...")

            try:
                description = self.glm_client.describe_image(image_path)
                image_descriptions.append({
                    'filename': filename,
                    'description': description
                })
                self.logger.info(f"  ✓ {description[:100]}...")
            except Exception as e:
                self.logger.error(f"  ❌ 描述失败: {e}")
                image_descriptions.append({
                    'filename': filename,
                    'description': f"描述失败: {str(e)}"
                })

        self.logger.info(f"\n✅ Stage 3 完成! 描述了 {len(image_descriptions)} 张图片")

        return image_descriptions

    def _stage4_match_placeholders(
        self,
        markdown: str,
        placeholders: List[Dict],
        image_descriptions: List[Dict]
    ) -> Dict[int, str]:
        """Stage 4: 使用DeepSeek进行语义匹配"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 4: DeepSeek 语义匹配")
        self.logger.info("=" * 60)

        # 从config加载提示词模板
        prompt_template = self.config.get('prompts', {}).get('semantic_matching')

        mapping = self.deepseek_client.semantic_matching(
            markdown,
            placeholders,
            image_descriptions,
            prompt_template
        )

        return mapping

    def _stage5_replace_placeholders(
        self,
        markdown: str,
        placeholders: List[Dict],
        mapping: Dict[int, str],
        output_dir: str
    ) -> str:
        """Stage 5: 替换占位符为实际图片路径"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 5: 替换占位符为图片路径")
        self.logger.info("=" * 60)

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
                self.logger.info(f"  ✓ 替换占位符 {idx} → {image_path}")
            else:
                # 移除未匹配的占位符
                markdown = markdown.replace(full_match, '')
                self.logger.warning(f"  ⚠️  移除未匹配的占位符 {idx}")

        self.logger.info(f"\n✅ Stage 5 完成! 所有占位符已处理")

        return markdown
