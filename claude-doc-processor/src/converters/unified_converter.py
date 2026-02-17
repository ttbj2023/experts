"""
统一文档转换器

核心设计理念：
- DOCX只是PDF的前体（通过LibreOffice转换）
- PDF→MD是通用流程
- 根据PDF类型选择不同分支：
  1. 文档型PDF（可提取嵌入图片，如DOCX转换的）
  2. 扫描型PDF（纯图像，需要OpenCV）

统一流程架构：
  - Stage 0: DOCX→PDF预处理（可选）
  - Stage 1: 文档解析（PDF类型检测）
  - Stage 2: 图片提取（分支选择）
  - Stage 3: OCR识别（GLM逐页）
  - Stage 3.5: 内容整理（DeepSeek逐页，可选）
  - Stage 4: 图片描述（GLM）
  - Stage 5: 语义匹配（DeepSeek全局）
  - Stage 6: 智能替换（去重+清理）
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF

from .base import BaseConverter
from ..core.glm_client import GLMClient
from ..core.deepseek_client import DeepSeekClient
from ..core.image_processor import ImageProcessor
from ..core.ocr_engine import OCREngine


class UnifiedConverter(BaseConverter):
    """
    统一文档转换器（v4统一架构）

    核心理念：
    - DOCX只是PDF的前体，PDF→MD是通用流程
    - 根据PDF类型智能选择处理策略
    - 支持逐页精修（Stage 3.5）
    """

    # PDF类型枚举
    PDF_TYPE_DOCUMENT = "document"  # 文档型PDF（可提取嵌入图片）
    PDF_TYPE_SCANNED = "scanned"    # 扫描型PDF（纯图像）

    def __init__(self, config_path: str = None):
        """初始化统一转换器"""
        super().__init__(config_path)

        # 初始化核心组件
        self.glm_client = GLMClient(self.config)
        self.deepseek_client = DeepSeekClient(self.config)
        self.image_processor = ImageProcessor(self.config)
        self.ocr_engine = OCREngine(self.config)

        # 处理配置
        self.detection_config = self.config.get('detection', {})
        self.pdf_config = self.config.get('processing', {}).get('pdf', {})
        self.docx_config = self.config.get('processing', {}).get('docx', {})

        # 开关配置
        self.enable_content_refinement = self.pdf_config.get('enable_content_refinement', False)  # Stage 3.5
        self.enable_code_cleanup = self.docx_config.get('enable_code_block_cleanup', True)
        self.enable_separator_cleanup = self.docx_config.get('enable_separator_cleanup', True)
        self.enable_duplicate_detection = self.docx_config.get('enable_duplicate_detection', True)

        # PDF处理参数
        self.dpi = self.pdf_config.get('dpi', 200)
        self.max_pages = self.pdf_config.get('max_pages', None)
        self.libreoffice_timeout = self.docx_config.get('libreoffice_timeout', 60)

    def convert(
        self,
        input_path: str,
        output_dir: str,
        max_pages: int = None,
        enable_content_refinement: bool = None
    ) -> Tuple[bool, str, Dict]:
        """
        执行文档到Markdown的统一转换流程

        Args:
            input_path: 输入文件路径（PDF或DOCX）
            output_dir: 输出目录
            max_pages: 最大处理页数（None表示全部）
            enable_content_refinement: 是否启用Stage 3.5内容整理

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self._start_timer()

        # 验证输入
        if not self._validate_input_file(input_path, ['.pdf', '.docx', '.doc']):
            return False, '', self.stats

        # 创建输出目录
        if not self._create_output_dir(output_dir):
            return False, '', self.stats

        # 更新配置
        if max_pages is None:
            max_pages = self.max_pages
        if enable_content_refinement is None:
            enable_content_refinement = self.enable_content_refinement

        self.logger.info("\n" + "=" * 70)
        self.logger.info("统一文档转换流程（v4架构）")
        self.logger.info("=" * 70)
        self.logger.info(f"输入: {input_path}")
        self.logger.info(f"输出: {output_dir}")
        self.logger.info(f"页数限制: {max_pages or '全部'}")
        self.logger.info(f"内容整理(Stage 3.5): {'启用' if enable_content_refinement else '禁用'}")

        try:
            # ========== Stage 0: DOCX→PDF预处理（可选） ==========
            pdf_path, docx_images = self._stage0_docx_to_pdf(input_path, output_dir)
            self.stats['stages_completed'].append('Stage 0: 文档预处理')

            # ========== Stage 1: 文档解析（PDF类型检测） ==========
            pdf_type = self._stage1_detect_pdf_type(pdf_path)
            self.stats['pdf_type'] = pdf_type
            self.stats['stages_completed'].append(f'Stage 1: PDF类型检测 ({pdf_type})')

            # ========== Stage 2: 图片提取（分支选择） ==========
            all_images = self._stage2_extract_images(
                pdf_path, output_dir, docx_images, pdf_type, max_pages
            )
            self.stats['total_images'] = len(all_images)
            self.stats['stages_completed'].append(f'Stage 2: 图片提取 ({len(all_images)}张)')

            # ========== Stage 3: OCR识别（GLM逐页） ==========
            markdown_pages, all_placeholders = self._stage3_ocr_pages(
                pdf_path, max_pages, enable_content_refinement
            )
            self.stats['stages_completed'].append('Stage 3: OCR识别')

            # 合并所有页面
            markdown = '\n\n'.join(markdown_pages)

            # 保存中间结果（OCR原始输出）
            raw_md_path = os.path.join(output_dir, 'stage3_raw_ocr.md')
            with open(raw_md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            # ========== Stage 4: 图片描述（GLM） ==========
            if all_images:
                image_descriptions = self._stage4_describe_images(all_images)
                self.stats['stages_completed'].append('Stage 4: 图片描述')
            else:
                image_descriptions = []
                self.logger.info("⚡ Stage 4: 无需图片描述（跳过）")

            # ========== Stage 5: 语义匹配（DeepSeek全局） ==========
            if all_placeholders and image_descriptions:
                mapping = self._stage5_semantic_matching(markdown, all_placeholders, image_descriptions)
                self.stats['matched_images'] = len(mapping)
                self.stats['stages_completed'].append(f'Stage 5: 语义匹配 ({len(mapping)}/{len(all_placeholders)})')
            else:
                mapping = {}
                self.logger.info("⚡ Stage 5: 无需语义匹配（跳过）")

            # ========== Stage 6: 智能替换 ==========
            images_dir = os.path.join(output_dir, 'images')
            final_markdown = self._stage6_smart_replacement(
                markdown,
                mapping,
                images_dir
            )
            self.stats['stages_completed'].append('Stage 6: 智能替换')

            # 保存最终结果
            output_file = self._get_output_filename(input_path, output_dir)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            # 保存元数据
            self._save_metadata(output_dir, input_path, output_file, len(all_images), len(mapping))

            self._stop_timer()
            self.stats['success'] = True

            return True, output_file, self.stats

        except Exception as e:
            self.logger.error(f"❌ 转换失败: {e}", exc_info=True)
            self.stats['success'] = False
            self.stats['error'] = str(e)
            return False, '', self.stats

    # ============================================================
    # Stage 0: DOCX→PDF预处理
    # ============================================================

    def _stage0_docx_to_pdf(
        self,
        input_path: str,
        output_dir: str
    ) -> Tuple[str, List[Dict]]:
        """
        Stage 0: DOCX→PDF预处理

        只对DOCX文件执行，PDF文件直接返回
        同时提取DOCX中的嵌入图片
        """
        # 检测文件类型
        if input_path.lower().endswith('.pdf'):
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Stage 0: 文档预处理（跳过，已是PDF）")
            self.logger.info("=" * 60)
            return input_path, []

        # DOCX文件
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 0: DOCX→PDF预处理")
        self.logger.info("=" * 60)

        basename = Path(input_path).stem
        pdf_path = os.path.join(output_dir, f'{basename}.pdf')
        images_dir = os.path.join(output_dir, 'docx_extracted_images')

        # 提取DOCX嵌入图片
        self.logger.info("  步骤0.1: 提取DOCX嵌入图片...")
        docx_images, _ = self.image_processor.extract_from_docx(input_path, images_dir)
        self.logger.info(f"  ✓ 提取了 {len(docx_images)} 张嵌入图片")

        # LibreOffice转换
        self.logger.info("  步骤0.2: LibreOffice转换（DOCX→PDF）...")
        try:
            result = subprocess.run(
                [
                    'soffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', output_dir,
                    input_path
                ],
                timeout=self.libreoffice_timeout,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and os.path.exists(pdf_path):
                self.logger.info(f"  ✓ 转换成功: {pdf_path}")
                return pdf_path, docx_images
            else:
                raise Exception(f"LibreOffice转换失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise Exception(f"LibreOffice转换超时（>{self.libreoffice_timeout}秒）")
        except Exception as e:
            raise Exception(f"LibreOffice转换失败: {e}")

    # ============================================================
    # Stage 1: 文档解析（PDF类型检测）
    # ============================================================

    def _stage1_detect_pdf_type(self, pdf_path: str) -> str:
        """
        Stage 1: PDF类型检测

        检测PDF类型：
        - document: 文档型PDF（可提取嵌入图片）
        - scanned: 扫描型PDF（纯图像）
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 1: PDF类型检测")
        self.logger.info("=" * 60)

        # 打开PDF
        doc = fitz.open(pdf_path)

        # 检测文本密度
        text_threshold = self.detection_config.get('pdf', {}).get('text_threshold', 1000)
        min_text_ratio = self.detection_config.get('pdf', {}).get('min_text_ratio', 0.1)

        # 采样前5页
        sample_pages = min(5, len(doc))
        total_text_chars = 0
        total_page_area = 0

        for page_num in range(sample_pages):
            page = doc[page_num]
            text = page.get_text()
            total_text_chars += len(text)

            # 计算页面面积（像素）
            rect = page.rect
            page_area = rect.width * rect.height
            total_page_area += page_area

        doc.close()

        # 计算文本密度
        avg_text_chars = total_text_chars / sample_pages
        text_ratio = total_text_chars / total_page_area if total_page_area > 0 else 0

        self.logger.info(f"  检测结果:")
        self.logger.info(f"    - 平均每页文本字符数: {avg_text_chars:.0f}")
        self.logger.info(f"    - 文本密度比: {text_ratio:.4f}")
        self.logger.info(f"    - 阈值: >={text_threshold}字符 且 >={min_text_ratio}密度")

        # 判断类型
        if avg_text_chars >= text_threshold and text_ratio >= min_text_ratio:
            pdf_type = self.PDF_TYPE_DOCUMENT
            self.logger.info(f"  ✓ 判定为: 文档型PDF（可提取嵌入图片）")
        else:
            pdf_type = self.PDF_TYPE_SCANNED
            self.logger.info(f"  ✓ 判定为: 扫描型PDF（纯图像）")

        return pdf_type

    # ============================================================
    # Stage 2: 图片提取（分支选择）
    # ============================================================

    def _stage2_extract_images(
        self,
        pdf_path: str,
        output_dir: str,
        docx_images: List[Dict],
        pdf_type: str,
        max_pages: int = None
    ) -> List[Dict]:
        """
        Stage 2: 图片提取（分支选择）

        根据PDF类型选择提取策略：
        - 文档型：使用DOCX提取的图片（如果有）
        - 扫描型：使用OpenCV提取
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 2: 图片提取（分支选择）")
        self.logger.info("=" * 60)
        self.logger.info(f"  PDF类型: {pdf_type}")

        # 分支1: 文档型PDF + 有DOCX图片 → 使用DOCX图片
        if pdf_type == self.PDF_TYPE_DOCUMENT and docx_images:
            self.logger.info(f"  策略: 使用DOCX嵌入图片（{len(docx_images)}张）")
            return docx_images

        # 分支2: 扫描型PDF 或 无DOCX图片 → OpenCV提取
        self.logger.info("  策略: OpenCV精确提取")
        images = self.image_processor.extract_from_pdf(
            pdf_path,
            output_dir,
            self.dpi,
            max_pages,
            use_opencv=True
        )

        return images

    # ============================================================
    # Stage 3: OCR识别（GLM逐页）
    # ============================================================

    def _stage3_ocr_pages(
        self,
        pdf_path: str,
        max_pages: int = None,
        enable_content_refinement: bool = False
    ) -> Tuple[List[str], List[Dict]]:
        """
        Stage 3: OCR识别（GLM逐页）

        逐页OCR识别，可选Stage 3.5内容整理

        Returns:
            (markdown页面列表, 所有占位符列表)
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 3: OCR识别（GLM逐页）")
        if enable_content_refinement:
            self.logger.info("  + Stage 3.5: 逐页内容整理（启用）")
        self.logger.info("=" * 60)

        # 打开PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        # 限制页数
        if max_pages is None:
            max_pages = total_pages
        else:
            max_pages = min(max_pages, total_pages)

        markdown_pages = []
        all_placeholders = []

        # 逐页处理
        for page_num in range(max_pages):
            self.logger.info(f"\n处理第 {page_num + 1}/{max_pages} 页...")

            page = doc[page_num]

            # 渲染为图片并保存到临时文件
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                pix.save(tmp_path)

            # Stage 3: GLM OCR识别
            self.logger.info(f"  Stage 3: GLM OCR识别...")
            try:
                page_markdown = self.glm_client.ocr_page(tmp_path)
            finally:
                # 清理临时文件
                try:
                    os.unlink(tmp_path)
                except:
                    pass

            # 统计占位符
            page_placeholders = self._extract_placeholders(page_markdown)
            self.logger.info(f"  ✓ OCR完成，提取到 {len(page_placeholders)} 个图片占位符")
            all_placeholders.extend(page_placeholders)

            # Stage 3.5: 内容整理（可选）
            if enable_content_refinement:
                self.logger.info(f"  Stage 3.5: DeepSeek内容整理...")
                page_markdown = self._format_page_with_deepseek(page_markdown, page_num + 1)
                self.logger.info(f"  ✓ 内容整理完成")

            markdown_pages.append(page_markdown)

        doc.close()

        self.logger.info(f"\n✅ Stage 3 完成!")
        self.logger.info(f"  总共识别: {max_pages} 页")
        self.logger.info(f"  图片占位符: {len(all_placeholders)} 个")

        return markdown_pages, all_placeholders

    def _format_page_with_deepseek(self, page_markdown: str, page_num: int) -> str:
        """
        Stage 3.5: 单页内容整理（DeepSeek）

        逐页优化格式，修正OCR错误
        """
        prompt_template = self.config.get('prompts', {}).get('markdown_formatting')

        # 添加页码上下文
        prompt = f"""{prompt_template}

这是第 {page_num} 页的内容。请进行格式优化和错误修正。"""

        formatted = self.deepseek_client.format_markdown(page_markdown, prompt)

        return formatted

    # ============================================================
    # Stage 4: 图片描述（GLM）
    # ============================================================

    def _stage4_describe_images(self, images: List[Dict]) -> List[Dict]:
        """
        Stage 4: 图片描述（GLM）

        为所有图片生成详细描述
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 4: 图片描述（GLM）")
        self.logger.info("=" * 60)

        image_descriptions = []

        for idx, img_info in enumerate(images, 1):
            filename = img_info['filename']
            image_path = img_info['path']

            self.logger.info(f"  [{idx}/{len(images)}] 描述图片: {filename}")

            # GLM描述（直接传递文件路径）
            description = self.glm_client.describe_image(image_path)

            image_descriptions.append({
                'filename': filename,
                'path': image_path,
                'page': img_info.get('page', 0),
                'description': description
            })

            self.logger.info(f"    ✓ {description[:50]}...")

        return image_descriptions

    # ============================================================
    # Stage 5: 语义匹配（DeepSeek全局）
    # ============================================================

    def _stage5_semantic_matching(
        self,
        markdown: str,
        placeholders: List[Dict],
        image_descriptions: List[Dict]
    ) -> Dict[str, str]:
        """
        Stage 5: 语义匹配（DeepSeek全局）

        使用完整文档上下文进行占位符↔图片匹配
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 5: 语义匹配（DeepSeek全局）")
        self.logger.info("=" * 60)
        self.logger.info(f"  占位符: {len(placeholders)} 个")
        self.logger.info(f"  图片描述: {len(image_descriptions)} 张")

        prompt_template = self.config.get('prompts', {}).get('semantic_matching')

        mapping = self.deepseek_client.semantic_matching(
            markdown,
            placeholders,
            image_descriptions,
            prompt_template
        )

        self.logger.info(f"  ✓ 匹配成功: {len(mapping)} 对")

        return mapping

    # ============================================================
    # Stage 6: 智能替换
    # ============================================================

    def _stage6_smart_replacement(
        self,
        markdown: str,
        mapping: Dict[str, str],
        images_dir: str
    ) -> str:
        """
        Stage 6: 智能替换

        去重、清理、替换占位符
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Stage 6: 智能替换")
        self.logger.info("=" * 60)

        final_markdown = markdown

        # 1. 代码块清理
        if self.enable_code_cleanup:
            self.logger.info("  步骤6.1: 代码块清理...")
            final_markdown = self._cleanup_code_blocks(final_markdown)

        # 2. 分隔符清理
        if self.enable_separator_cleanup:
            self.logger.info("  步骤6.2: 分隔符清理...")
            final_markdown = self._cleanup_separators(final_markdown)

        # 3. 占位符替换
        self.logger.info(f"  步骤6.3: 占位符替换（{len(mapping)}个）...")
        final_markdown = self._replace_placeholders(final_markdown, mapping, images_dir)

        # 4. 重复检测（可选）
        if self.enable_duplicate_detection:
            self.logger.info("  步骤6.4: 重复检测...")
            final_markdown = self._detect_duplicates(final_markdown)

        self.logger.info("  ✓ 智能替换完成")

        return final_markdown

    # ============================================================
    # 辅助方法
    # ============================================================

    def _extract_placeholders(self, markdown: str) -> List[Dict]:
        """从Markdown中提取所有图片占位符"""
        import re

        pattern = r'<!--\s*IMAGE_PLACEHOLDER\s+(.*?)-->'
        matches = re.findall(pattern, markdown, re.DOTALL)

        placeholders = []
        for idx, match in enumerate(matches, 1):
            # 解析占位符属性
            attrs = {}
            for line in match.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    attrs[key.strip()] = value.strip()

            placeholders.append({
                'index': idx,  # DeepSeekClient期望的键
                'page': 0,     # 暂时设置为0，后续可以优化
                'id': idx,     # 保留兼容性
                'raw': match,
                'type': attrs.get('type', 'unknown'),
                'description': attrs.get('description', '')
            })

        return placeholders

    def _cleanup_code_blocks(self, markdown: str) -> str:
        """清理错误的代码块"""
        import re

        # 移除空代码块
        markdown = re.sub(r'```\s*```', '', markdown)

        return markdown

    def _cleanup_separators(self, markdown: str) -> str:
        """清理多余的分隔符"""
        import re

        # 移除连续的多个水平线（保留一个）
        markdown = re.sub(r'(---\n){3,}', '---\n', markdown)

        return markdown

    def _replace_placeholders(
        self,
        markdown: str,
        mapping: Dict[str, str],
        images_dir: str
    ) -> str:
        """替换占位符为Markdown图片语法"""
        import re

        for placeholder_id, image_filename in mapping.items():
            # 构建占位符正则
            pattern = f'<!--\\s*IMAGE_PLACEHOLDER[^>]*id:\\s*{placeholder_id}[^>]*-->'

            # 构建Markdown图片语法（使用相对路径）
            image_path = os.path.join('images', image_filename)

            replacement = f'\n![{image_filename}]({image_path})\n'

            markdown = re.sub(pattern, replacement, markdown, flags=re.DOTALL)

        return markdown

    def _detect_duplicates(self, markdown: str) -> str:
        """检测并移除重复内容"""
        # TODO: 实现重复检测逻辑
        return markdown

    def _get_output_filename(self, input_path: str, output_dir: str) -> str:
        """生成输出文件名"""
        basename = Path(input_path).stem
        return os.path.join(output_dir, f'{basename}.md')

    def _save_metadata(
        self,
        output_dir: str,
        input_path: str,
        output_file: str,
        total_images: int,
        matched_images: int
    ):
        """保存元数据"""
        import json
        from datetime import datetime

        metadata = {
            'converter': 'UnifiedConverter',
            'version': 'v4',
            'timestamp': datetime.now().isoformat(),
            'processing_time_seconds': self.stats.get('processing_time', 0),
            'input_file': input_path,
            'output_file': output_file,
            'pdf_type': self.stats.get('pdf_type', 'unknown'),
            'statistics': {
                'total_images': total_images,
                'matched_images': matched_images,
                'stages_completed': self.stats.get('stages_completed', [])
            }
        }

        meta_file = os.path.join(output_dir, 'meta.json')
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        self.logger.info(f"💾 元数据已保存: {meta_file}")
