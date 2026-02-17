#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Markdown Converter with Images - 智能分类版本

适用范围：
- 文字PDF（Word/出版软件转换）：直接提取原始嵌入图片
- 扫描件PDF：使用GLM-4.6V-Flash识别插图位置并裁剪
- 数学、物理、化学、工程等科技文档
- 教材、论文、技术手册、报告等

三阶段架构（复用v3流程）：
1. Stage 1: 智能图片提取 + GLM-4.6V-Flash PDF识别（带占位符）
2. Stage 2: GLM-4V → 描述所有提取的图片
3. Stage 3: DeepSeek → 语义匹配占位符与图片描述
4. Stage 4: 替换占位符为正确的图片URL

核心特性：
- 自动检测PDF类型（文字PDF vs 扫描件PDF）
- 针对不同类型使用最优图片提取方式
- 复用convert_docx_to_markdown_v3.py的成熟流程
- 支持扫描件出版物的智能插图提取
"""

import os
import sys
import json
import subprocess
import shutil
import logging
import re
import base64
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from PIL import Image
import io
import fitz  # PyMuPDF - PDF处理库

# 添加utils目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFTypeDetector:
    """PDF类型检测器 - 自动识别文字PDF还是扫描件PDF"""

    @staticmethod
    def detect(pdf_path: str) -> str:
        """
        检测PDF类型

        Args:
            pdf_path: PDF文件路径

        Returns:
            'document': 文字PDF（有原始图片对象，可直接提取）
            'scanned': 扫描件PDF（纯图像，需要GLM识别插图）
        """
        try:
            pdf = fitz.open(pdf_path)

            # 检查前3页（如果有的话）
            max_pages_to_check = min(3, len(pdf))
            has_images = 0
            total_text_length = 0

            for page_num in range(max_pages_to_check):
                page = pdf[page_num]

                # 检查1: 是否有原始图片对象
                page_images = page.get_images()
                if len(page_images) > 0:
                    has_images += 1

                # 检查2: 是否有可选择文字
                text_content = page.get_text("text")
                total_text_length += len(text_content.strip())

            pdf.close()

            # 判断逻辑
            avg_text_per_page = total_text_length / max_pages_to_check

            # 如果平均每页文字少于50字符，认为是扫描件
            if avg_text_per_page < 50:
                return 'scanned'

            # 如果有多页都有图片对象，认为是文字PDF
            if has_images >= max_pages_to_check // 2:
                return 'document'

            # 默认：文字PDF（可能没有图片或只有少量图片）
            return 'document'

        except Exception as e:
            logger.warning(f"PDF类型检测失败: {e}，默认使用document模式")
            return 'document'


class PDFToMarkdownConverter:
    """PDF到Markdown转换器 - 智能分类版本（支持扫描件插图提取）"""

    def __init__(self,
                 output_base_dir: str = "output_pdf_to_md",
                 mineru_api_url: str = "http://localhost:8001",
                 glm_api_url: str = "http://192.168.100.110:9999",
                 glm_api_key: str = None,
                 deepseek_api_key: str = None):
        """
        初始化转换器

        Args:
            output_base_dir: 输出基础目录
            mineru_api_url: MinerU服务地址（暂未使用，保留兼容性）
            glm_api_url: GLM-4.6V-Flash服务地址
            glm_api_key: GLM-4V API密钥
            deepseek_api_key: DeepSeek API密钥
        """
        self.output_base_dir = output_base_dir
        self.mineru_api_url = mineru_api_url
        self.glm_api_url = glm_api_url
        self.glm_api_key = glm_api_key or os.getenv("GLM_API_KEY", "5810137ffe1d4ed6b540c9e9dba75a1c.rcc0w7weFkYO4QDb")
        self.deepseek_api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY", "sk-62f31b03e22048799beefff7cae0dfc3")

        # 转换统计
        self.stats = {
            'input_file': '',
            'output_dir': '',
            'stage1_success': False,
            'stage1_time': 0,
            'stage2_success': False,
            'stage2_time': 0,
            'stage3_success': False,
            'stage3_time': 0,
            'total_placeholders': 0,
            'total_images': 0,
            'matched_images': 0,
            'unmatched_placeholders': 0,
            'processing_time': 0,
            'success': False,
            'error': None
        }

    def convert(self, input_file: str) -> Tuple[bool, str, dict]:
        """
        转换PDF文件为Markdown（三阶段架构，支持扫描件插图提取）

        Args:
            input_file: 输入PDF文件路径

        Returns:
            (success, output_path, stats): 是否成功、输出路径、统计信息
        """
        start_time = datetime.now()

        # 验证输入文件
        if not os.path.exists(input_file):
            error_msg = f"输入文件不存在: {input_file}"
            logger.error(error_msg)
            return False, '', {'error': error_msg}

        if not input_file.lower().endswith('.pdf'):
            error_msg = f"输入文件不是PDF格式: {input_file}"
            logger.error(error_msg)
            return False, '', {'error': error_msg}

        # 设置输出路径
        file_name = Path(input_file).stem
        output_dir = os.path.join(self.output_base_dir, file_name)
        os.makedirs(output_dir, exist_ok=True)

        # 临时文件路径
        temp_md = os.path.join(output_dir, '_temp_with_placeholders.md')
        output_md = os.path.join(output_dir, 'document.md')
        meta_json = os.path.join(output_dir, 'meta.json')
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)

        logger.info("=" * 80)
        logger.info("PDF to Markdown Converter - 智能分类版本（支持扫描件插图）")
        logger.info("=" * 80)
        logger.info(f"输入文件: {input_file}")
        logger.info(f"输出目录: {output_dir}")

        self.stats['input_file'] = input_file
        self.stats['output_dir'] = output_dir

        try:
            # Stage 1: 智能图片提取 + GLM-4.6V-Flash PDF识别（生成占位符）
            logger.info("\n" + "=" * 80)
            logger.info("Stage 1: 智能图片提取 + GLM-4.6V-Flash PDF识别")
            logger.info("=" * 80)

            stage1_start = datetime.now()
            markdown_with_placeholders, pdf_images = self._stage1_extract_images_and_recognize(input_file, temp_md, images_dir)
            self.stats['stage1_time'] = (datetime.now() - stage1_start).total_seconds()
            self.stats['stage1_success'] = True
            self.stats['total_images'] = len(pdf_images)

            # Stage 2: GLM-4V → 描述所有提取的图片
            logger.info("\n" + "=" * 80)
            logger.info("Stage 2: GLM-4V 图片描述生成")
            logger.info("=" * 80)

            stage2_start = datetime.now()
            image_descriptions = self._stage2_describe_images(pdf_images, images_dir)
            self.stats['stage2_time'] = (datetime.now() - stage2_start).total_seconds()
            self.stats['stage2_success'] = True

            # Stage 3: DeepSeek → 语义匹配占位符与图片
            logger.info("\n" + "=" * 80)
            logger.info("Stage 3: DeepSeek 语义匹配")
            logger.info("=" * 80)

            stage3_start = datetime.now()
            placeholder_mapping = self._stage3_semantic_matching(temp_md, image_descriptions)
            self.stats['stage3_time'] = (datetime.now() - stage3_start).total_seconds()
            self.stats['stage3_success'] = True
            self.stats['matched_images'] = len(placeholder_mapping)

            # Stage 4: 替换占位符为图片URL
            logger.info("\n" + "=" * 80)
            logger.info("Stage 4: 替换占位符为图片URL")
            logger.info("=" * 80)

            final_markdown = self._stage4_replace_placeholders(temp_md, placeholder_mapping, images_dir, image_descriptions)

            # 保存最终Markdown
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
            logger.info(f"✓ 已保存最终Markdown: {output_md}")

            # 保存中间结果
            intermediate_results = {
                'stage1_markdown_with_placeholders': temp_md,
                'stage2_image_descriptions': os.path.join(output_dir, 'image_descriptions.json'),
                'stage3_matching_result': os.path.join(output_dir, 'matching_result.json')
            }

            # 保存图片描述
            with open(intermediate_results['stage2_image_descriptions'], 'w', encoding='utf-8') as f:
                json.dump(image_descriptions, f, ensure_ascii=False, indent=2)

            # 保存匹配结果
            with open(intermediate_results['stage3_matching_result'], 'w', encoding='utf-8') as f:
                json.dump(placeholder_mapping, f, ensure_ascii=False, indent=2)

            # 生成元数据
            self.stats['success'] = True
            self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()

            with open(meta_json, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)

            logger.info("\n" + "=" * 80)
            logger.info("转换成功！")
            logger.info(f"  输出文件: {output_md}")
            logger.info(f"  总图片数: {self.stats['total_images']}")
            logger.info(f"  匹配成功: {self.stats['matched_images']}")
            logger.info(f"  Stage 1耗时: {self.stats['stage1_time']:.2f}秒")
            logger.info(f"  Stage 2耗时: {self.stats['stage2_time']:.2f}秒")
            logger.info(f"  Stage 3耗时: {self.stats['stage3_time']:.2f}秒")
            logger.info(f"  总耗时: {self.stats['processing_time']:.2f}秒")
            logger.info("=" * 80)

            return True, output_md, self.stats

        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.stats['success'] = False
            self.stats['error'] = error_msg
            self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()

            # 保存错误信息
            try:
                with open(meta_json, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, ensure_ascii=False, indent=2)
            except:
                pass

            return False, '', self.stats

    def _stage1_extract_images_and_recognize(self, pdf_path: str, md_path: str, images_dir: str) -> Tuple[str, List[Dict]]:
        """
        Stage 1: 智能图片提取 + GLM-4.6V-Flash PDF识别（生成带占位符的Markdown）

        Args:
            pdf_path: PDF文件路径
            md_path: 输出的Markdown文件路径
            images_dir: 图片输出目录

        Returns:
            (markdown_content, images): Markdown内容和提取的图片列表
        """
        # 步骤1.1: 检测PDF类型
        logger.info("  步骤1.1: 检测PDF类型...")
        pdf_type = PDFTypeDetector.detect(pdf_path)
        logger.info(f"  ✓ PDF类型: {pdf_type}")

        # 步骤1.2: 根据类型提取图片
        logger.info(f"  步骤1.2: 提取图片（{pdf_type}模式）...")
        if pdf_type == 'document':
            # 文字PDF：直接提取原始图片
            images = self._extract_images_from_document_pdf(pdf_path, images_dir)
        else:
            # 扫描件PDF：使用GLM-4.6V-Flash识别插图
            images = self._extract_images_from_scanned_pdf(pdf_path, images_dir)

        logger.info(f"  ✓ 提取了 {len(images)} 张图片")

        # 步骤1.3: PDF → Markdown (GLM-4.6V-Flash with placeholders)
        logger.info("  步骤1.3: PDF → Markdown (GLM-4.6V-Flash)...")
        markdown_content = self._convert_pdf_with_glm46v(pdf_path, md_path)
        logger.info(f"  ✓ Markdown生成成功（带占位符）")

        return markdown_content, images

    def _stage2_describe_images(self, images: List[Dict], images_dir: str) -> List[Dict]:
        """
        Stage 2: 使用GLM-4V描述所有提取的图片

        Args:
            images: 图片信息列表
            images_dir: 图片目录

        Returns:
            图片描述列表: [{
                'filename': 'image1.png',
                'description': '图片描述内容...'
            }]
        """
        logger.info(f"  开始描述 {len(images)} 张图片...")

        image_descriptions = []

        for idx, img_info in enumerate(images, 1):
            filename = img_info['filename']
            image_path = os.path.join(images_dir, filename)

            logger.info(f"  [{idx}/{len(images)}] 描述 {filename}...")

            try:
                description = self._describe_single_image(image_path)
                image_descriptions.append({
                    'filename': filename,
                    'description': description
                })
                logger.info(f"    ✓ {description[:100]}...")
            except Exception as e:
                logger.warning(f"    ⚠️  描述失败: {e}")
                image_descriptions.append({
                    'filename': filename,
                    'description': f"（图片描述失败: {str(e)}）"
                })

        logger.info(f"  ✓ 完成描述 {len(image_descriptions)} 张图片")

        return image_descriptions

    def _stage3_semantic_matching(self, md_path: str, image_descriptions: List[Dict]) -> Dict[int, str]:
        """
        Stage 3: 使用DeepSeek进行语义匹配（全局上下文模式）

        Returns:
            匹配映射: {placeholder_index: image_filename}
        """
        # 读取整个md文档内容（作为上下文）
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 提取占位符
        placeholders = self._extract_placeholders(md_path)
        logger.info(f"  找到 {len(placeholders)} 个占位符")
        logger.info(f"  找到 {len(image_descriptions)} 张图片描述")

        # 调用DeepSeek API进行匹配（传递完整文档上下文）
        logger.info("  调用DeepSeek API进行全局上下文语义匹配...")
        mapping = self._call_deepseek_for_matching_global(md_content, placeholders, image_descriptions)

        logger.info(f"  ✓ 匹配完成: {len(mapping)}/{len(placeholders)} 个占位符成功匹配")

        return mapping

    def _remove_invalid_code_blocks(self, content: str) -> str:
        """
        移除GLM-4.6V-Flash误识别的无效代码块

        策略：DOCX文档不应该有代码块，移除所有```标记
        - 保留代码块内的内容（ASCII art、公式等）
        - 只移除```标记本身
        """
        lines = content.split('\n')
        result_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # 检测代码块开始标记
            if line.strip().startswith('```'):
                # 找到代码块结束标记
                start_idx = i
                i += 1

                # 查找对应的结束标记
                end_idx = -1
                while i < len(lines):
                    if lines[i].strip() == '```':
                        end_idx = i
                        break
                    i += 1

                if end_idx == -1:
                    # 没有找到结束标记，保留这一行并继续
                    result_lines.append(line)
                    continue

                # 提取代码块内容并保留（移除```标记）
                code_content = '\n'.join(lines[start_idx + 1:end_idx])
                if code_content.strip():  # 如果内容不为空
                    # 去除每行的缩进（代码块内的内容通常有缩进）
                    # 找到最小缩进量
                    content_lines = code_content.split('\n')
                    min_indent = float('inf')
                    for line in content_lines:
                        if line.strip():  # 非空行
                            indent = len(line) - len(line.lstrip())
                            min_indent = min(min_indent, indent)

                    # 去除最小缩进量
                    if min_indent > 0 and min_indent != float('inf'):
                        dedented_lines = [line[min_indent:] if len(line) >= min_indent else line
                                         for line in content_lines]
                        code_content = '\n'.join(dedented_lines)

                    result_lines.append(code_content)

                i = end_idx + 1
            else:
                result_lines.append(line)
                i += 1

        return '\n'.join(result_lines)

    def _remove_pdf_page_separators(self, content: str) -> str:
        """
        移除GLM-4.6V-Flash添加的PDF页面分隔符

        策略：只移除"孤立的"页面分隔符，保留有实际用途的分隔符
        """
        import re

        lines = content.split('\n')
        result_lines = []

        for i, line in enumerate(lines):
            # 检查是否是页面分隔符
            if line.strip() == '---':
                # 检查前一行和后一行（如果存在）
                prev_line = lines[i - 1].strip() if i > 0 else ''
                next_line = lines[i + 1].strip() if i < len(lines) - 1 else ''

                # 判断是否是PDF页面分界符（孤立的"---"）
                # 特征：前后都是空行，或者是文档边界
                prev_is_empty = (i == 0) or (prev_line == '')
                next_is_empty = (i == len(lines) - 1) or (next_line == '')

                # 检查是否在代码块中（不删除代码块中的"---"）
                # 回溯查找最近的代码块标记
                in_code_block = False
                for j in range(i - 1, max(0, i - 50), -1):
                    if '```' in lines[j]:
                        in_code_block = True
                        break

                # 如果是孤立的页面分隔符，跳过（不添加到结果）
                if prev_is_empty and next_is_empty and not in_code_block:
                    # 这是PDF页面分界符，删除
                    continue
                else:
                    # 这是有实际用途的分隔符，保留
                    result_lines.append(line)
            else:
                # 普通内容，保留
                result_lines.append(line)

        return '\n'.join(result_lines)

    def _stage4_replace_placeholders(self, md_path: str, mapping: Dict[int, str], images_dir: str, image_descriptions: List[Dict] = None) -> str:
        """
        Stage 4: 替换占位符为图片URL

        Args:
            md_path: Markdown文件路径
            mapping: 占位符索引到图片文件名的映射
            images_dir: 图片目录
            image_descriptions: 图片描述列表（可选）

        Returns:
            最终Markdown内容
        """
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 移除无效的代码块（GLM-4.6V-Flash误识别的代码块）
        logger.info("  移除无效代码块...")
        code_blocks_before = content.count('```')
        content = self._remove_invalid_code_blocks(content)
        code_blocks_after = content.count('```')
        removed_code_blocks = code_blocks_before - code_blocks_after
        if removed_code_blocks > 0:
            logger.info(f"  ✓ 移除了 {removed_code_blocks // 2} 个无效代码块")

        # 移除PDF页面分隔符（DOCX流程不需要保留PDF页面结构）
        logger.info("  移除PDF页面分隔符...")
        content_before = len(content)
        content = self._remove_pdf_page_separators(content)
        removed = content_before - len(content)
        if removed > 0:
            logger.info(f"  ✓ 移除了 {content.count('---')} 个页面分隔符")
        else:
            logger.info("  ✓ 未检测到页面分隔符")

        # 替换占位符
        import re
        placeholder_pattern = r'<!--\s*IMAGE_PLACEHOLDER\s+type:\s*(.+?)\s*description:\s*(.+?)\s*-->'

        # 创建图片文件名到描述的映射
        filename_to_desc = {}
        if image_descriptions:
            for img_desc in image_descriptions:
                filename_to_desc[img_desc['filename']] = img_desc['description']

        # 检测同一张图片被匹配到多个占位符的情况
        # 统计每个图片被匹配的次数
        image_usage = {}
        for placeholder_idx, image_filename in mapping.items():
            if image_filename not in image_usage:
                image_usage[image_filename] = []
            image_usage[image_filename].append(placeholder_idx)

        # 找出被多次使用的图片
        duplicate_images = {img: indices for img, indices in image_usage.items() if len(indices) > 1}
        if duplicate_images:
            logger.warning(f"  ⚠️  检测到 {len(duplicate_images)} 张图片被匹配到多个占位符:")
            for img, indices in duplicate_images.items():
                logger.warning(f"      {img}: 占位符 {indices}")
                # 只在最后一个位置插入图片，其他位置移除占位符
                last_index = max(indices)
                for idx in indices:
                    if idx != last_index:
                        # 移除前面位置的匹配
                        del mapping[idx]
                        logger.warning(f"        → 移除占位符 {idx} 的匹配，只在占位符 {last_index} 保留")
            logger.info(f"  ✓ 处理重复匹配后，剩余 {len(mapping)} 个占位符需要替换")

        def replace_placeholder(match):
            # 获取这是第几个占位符
            all_matches = list(re.finditer(placeholder_pattern, content, re.DOTALL))
            for idx, m in enumerate(all_matches):
                if m.start() == match.start():
                    # 找到对应的图片
                    if idx in mapping:
                        image_filename = mapping[idx]
                        image_url = f"./images/{image_filename}"
                        return f"\n![图片]({image_url})\n"
            return match.group(0)  # 未匹配，保留原样

        # 按顺序替换占位符（从后往前，避免位置偏移）
        matches = list(re.finditer(placeholder_pattern, content, re.DOTALL))
        removed_count = 0
        for match in reversed(matches):
            placeholder_text = match.group(0)
            # 计算这是第几个占位符
            placeholder_index = len([m for m in matches if m.start() <= match.start()]) - 1

            if placeholder_index in mapping:
                image_filename = mapping[placeholder_index]
                image_url = f"./images/{image_filename}"

                # 提取占位符中的原始描述（如果需要）
                placeholder_desc = None
                placeholder_match = re.search(placeholder_pattern, placeholder_text)
                if placeholder_match:
                    placeholder_desc = placeholder_match.group(2).strip()

                # 优先使用GLM-4V的详细描述，如果没有则使用占位符中的描述
                full_description = None
                if image_filename in filename_to_desc:
                    full_description = filename_to_desc[image_filename]

                # 如果有详细描述，使用详细描述；否则使用占位符描述
                if full_description:
                    # 使用完整描述（GLM-4V生成的详细描述）
                    alt_text = f"图片：{full_description}"
                elif placeholder_desc:
                    # 使用占位符中的描述
                    alt_text = f"图片：{placeholder_desc}"
                else:
                    # 没有描述，使用默认文本
                    alt_text = "图片"

                replacement = f"\n![{alt_text}]({image_url})\n"
                content = content[:match.start()] + replacement + content[match.end():]
                logger.info(f"  ✓ 替换占位符 {placeholder_index} → {image_filename}")
            else:
                # 未匹配的占位符（包括被重复检测移除的），直接删除
                content = content[:match.start()] + '' + content[match.end():]
                removed_count += 1
                logger.info(f"  ○ 移除占位符 {placeholder_index}（未匹配或已被去重）")

        logger.info(f"  ✓ 替换了 {len(mapping)} 个占位符，移除了 {removed_count} 个未匹配占位符")

        return content

    def _extract_images_from_document_pdf(self, pdf_path: str, images_dir: str) -> List[Dict]:
        """
        从文字PDF（Word/出版软件转换的）提取原始嵌入图片

        Args:
            pdf_path: PDF文件路径
            images_dir: 图片输出目录

        Returns:
            图片信息列表
        """
        logger.info("    使用document模式：直接提取原始图片...")
        pdf = fitz.open(pdf_path)
        images = []

        try:
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                image_list = page.get_images()

                for img_index, img in enumerate(image_list, 1):
                    try:
                        xref = img[0]
                        base_image = pdf.extract_image(xref)

                        # 保存图片
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        filename = f"page{page_num+1:03d}_img{img_index:02d}.{image_ext}"
                        filepath = os.path.join(images_dir, filename)

                        with open(filepath, "wb") as f:
                            f.write(image_bytes)

                        images.append({
                            'filename': filename,
                            'page': page_num + 1,
                            'width': base_image['width'],
                            'height': base_image['height'],
                            'size': len(image_bytes)
                        })

                        logger.debug(f"      提取: {filename} ({base_image['width']}x{base_image['height']})")

                    except Exception as e:
                        logger.warning(f"      提取图片失败: {e}")
                        continue

        finally:
            pdf.close()

        logger.info(f"    ✓ 提取了 {len(images)} 张原始图片")
        return images

    def _extract_images_from_scanned_pdf(self, pdf_path: str, images_dir: str) -> List[Dict]:
        """
        从扫描件PDF提取插图（使用GLM-4.6V-Flash识别bbox并裁剪）

        Args:
            pdf_path: PDF文件路径
            images_dir: 图片输出目录

        Returns:
            图片信息列表
        """
        logger.info("    使用scanned模式：GLM-4.6V-Flash识别插图...")

        # 导入GLM处理器
        import sys
        script_path = os.path.join(os.path.dirname(__file__), 'process_pdf_with_glm46v_v2.py')

        import importlib.util
        spec = importlib.util.spec_from_file_location("process_pdf_with_glm46v_v2", script_path)
        glm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(glm_module)

        processor = glm_module.GLM46VProcessor(api_url=self.glm_api_url)

        pdf = fitz.open(pdf_path)
        images = []

        try:
            for page_num in range(len(pdf)):
                logger.info(f"      处理第 {page_num + 1}/{len(pdf)} 页...")

                # 1. 获取高分辨率页面图片
                page = pdf[page_num]
                mat = fitz.Matrix(300/72, 300/72)  # 300 DPI保证裁剪质量
                pix = page.get_pixmap(matrix=mat)
                page_img_path = os.path.join(images_dir, f"_temp_page_{page_num+1:03d}.png")
                pix.save(page_img_path)

                # 2. 使用GLM-4.6V-Flash识别插图位置和类型
                prompt = """请分析这个扫描页面，**只提取需要用图片呈现的内容**。

**需要提取为图片的**：
1. 几何图形：三角形、圆、多边形、立体几何图
2. 函数图像：坐标系、曲线、函数图像
3. 统计图表：柱状图、饼图、折线图、散点图
4. 示意图：流程图、结构图、示意图

**不要提取**（这些用Markdown/LaTeX表达）：
- ❌ 文字段落
- ❌ 数学公式
- ❌ 数据表格（转Markdown表格）
- ❌ 页眉页脚

**输出格式**（纯JSON，不要其他内容）：
```json
[
  {
    "type": "geometry",
    "description": "triangle_with_height",
    "bbox": [x0, y0, x1, y1]
  }
]
```

**注意**：
- bbox格式：[x0, y0, x1, y1]，单位像素，左上角为原点
- 如果页面没有插图，返回空数组 []
"""

                try:
                    image_base64 = processor.compress_image(page_img_path, compression="medium")
                    response = processor.call_glm46v_api(image_base64, prompt, max_tokens=4096)
                    content = response["choices"][0]["message"]["content"]

                    # 3. 解析JSON
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        json_str = content.strip()

                    illustrations = json.loads(json_str)

                    # 4. 裁剪并保存插图
                    for idx, ill in enumerate(illustrations, 1):
                        bbox = ill['bbox']
                        ill_type = ill['type']
                        desc = ill.get('description', f'ill{idx}')

                        # 裁剪（添加10像素边缘）
                        margin = 10
                        x0 = max(0, bbox[0] - margin)
                        y0 = max(0, bbox[1] - margin)
                        x1 = min(pix.width, bbox[2] + margin)
                        y1 = min(pix.height, bbox[3] + margin)

                        # 使用正确的PyMuPDF API：先获取Page，再从Pixmap裁剪
                        rect = fitz.Rect(x0, y0, x1, y1)

                        # 方法1：直接从Page获取指定区域的Pixmap
                        clipped_pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(300/72, 300/72))

                        # 保存
                        filename = f"page{page_num+1:03d}_{ill_type}_{desc}.png"
                        filepath = os.path.join(images_dir, filename)
                        clipped_pix.save(filepath)

                        images.append({
                            'filename': filename,
                            'page': page_num + 1,
                            'type': ill_type,
                            'description': desc,
                            'width': clipped_pix.width,
                            'height': clipped_pix.height
                        })

                        logger.info(f"        ✓ 提取: {filename} ({clipped_pix.width}x{clipped_pix.height}px)")

                except Exception as e:
                    logger.warning(f"        ⚠ 第{page_num+1}页插图识别失败: {e}")
                finally:
                    # 删除临时页面图片
                    if os.path.exists(page_img_path):
                        os.remove(page_img_path)

        finally:
            pdf.close()

        logger.info(f"    ✓ 提取了 {len(images)} 张插图")
        return images

    def _extract_images_from_docx(self, docx_path: str, images_dir: str) -> Tuple[List[Dict], int]:
        """从DOCX提取图片（复用v2的逻辑）"""
        from docx import Document

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

                    # 保存所有图片（不过滤，让DeepSeek自己判断哪些有用）

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

        return images, filtered_count

    def _convert_docx_to_pdf(self, docx_path: str, pdf_path: str) -> bool:
        """使用LibreOffice将DOCX转换为PDF"""
        try:
            output_dir = os.path.dirname(pdf_path)
            docx_name = Path(docx_path).stem  # 获取原文件名（不含扩展名）
            expected_pdf_name = f"{docx_name}.pdf"  # LibreOffice会使用原文件名
            expected_pdf_path = os.path.join(output_dir, expected_pdf_name)

            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                docx_path
            ]

            logger.info(f"执行命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )

            # LibreOffice会生成与原文件同名的PDF
            if result.returncode == 0 and os.path.exists(expected_pdf_path):
                # 重命名为期望的文件名
                if expected_pdf_path != pdf_path:
                    shutil.move(expected_pdf_path, pdf_path)
                    logger.info(f"PDF已重命名: {expected_pdf_path} → {pdf_path}")
                return True
            else:
                stderr_output = result.stderr.decode()
                # LibreOffice的javaldx警告可以忽略
                if "failed to launch javaldx" in stderr_output and result.returncode == 0:
                    logger.warning(f"LibreOffice出现javaldx警告（可忽略）")
                    if os.path.exists(expected_pdf_path):
                        if expected_pdf_path != pdf_path:
                            shutil.move(expected_pdf_path, pdf_path)
                        return True
                logger.error(f"LibreOffice转换失败: {stderr_output}")
                return False

        except Exception as e:
            logger.error(f"DOCX转PDF异常: {e}")
            return False

    def _convert_pdf_with_glm46v(self, pdf_path: str, md_path: str) -> str:
        """使用GLM-4.6V-Flash将PDF转换为Markdown（带占位符）"""
        # 导入GLM46VProcessor
        import sys
        script_path = os.path.join(os.path.dirname(__file__), 'process_pdf_with_glm46v_v2.py')

        # 动态导入模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("process_pdf_with_glm46v_v2", script_path)
        glm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(glm_module)

        # 创建处理器实例
        processor = glm_module.GLM46VProcessor(api_url=self.glm_api_url)

        # 处理PDF（获取输出目录）
        output_dir = os.path.dirname(md_path)
        logger.info(f"    调用GLM-4.6V-Flash处理PDF: {pdf_path}")

        generated_md_path = processor.process_pdf(pdf_path, output_dir=output_dir)

        # 读取生成的Markdown内容
        with open(generated_md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # 如果生成的文件路径与预期不同，复制到预期位置
        if generated_md_path != md_path:
            import shutil
            shutil.copy(generated_md_path, md_path)
            logger.info(f"    已复制Markdown到: {md_path}")

        return markdown_content

    def _describe_single_image(self, image_path: str, max_size: int = 1280) -> str:
        """使用GLM-4V描述单张图片"""
        # 压缩图片
        img = Image.open(image_path)
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # 转换图片模式以支持JPEG格式（JPEG不支持RGBA透明通道）
        if img.mode == 'RGBA':
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
            img = background
        elif img.mode not in ('RGB', 'L'):
            # 其他模式转换为RGB
            img = img.convert('RGB')

        # 转换为JPEG字节流
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        image_bytes = buffer.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # 调用GLM-4V API
        prompt = """请详细描述这张图片的内容。

要求：
1. 识别图片的类型（几何图形、数学公式、统计图表、示意图等）
2. 描述图片中的关键元素和细节
3. 如果有文字或标注，请准确引用
4. 描述要准确、简洁，不超过200字

请直接返回描述文本，不要添加其他内容。"""

        payload = {
            "model": "zai-org/glm-4.6v-flash",  # 使用实际加载的模型
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }

        response = requests.post(
            f"{self.glm_api_url}/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.glm_api_key}"
            },
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        description = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

        return description

    def _extract_placeholders(self, md_path: str) -> List[Dict]:
        """从Markdown中提取占位符"""
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        import re
        pattern = r'<!--\s*IMAGE_PLACEHOLDER\s+type:\s*(.+?)\s*description:\s*(.+?)\s*-->'
        matches = re.finditer(pattern, content, re.DOTALL)

        placeholders = []
        for idx, match in enumerate(matches):
            placeholders.append({
                'index': idx,
                'type': match.group(1).strip(),
                'description': match.group(2).strip()
            })

        return placeholders

    def _call_deepseek_for_matching(self, placeholders: List[Dict], image_descriptions: List[Dict]) -> Dict[int, str]:
        """调用DeepSeek API进行语义匹配"""
        # 构建prompt
        prompt = """你是一个智能文档处理助手，负责将图片占位符与实际图片进行语义匹配。

## 任务说明
我会给你：
1. 一组图片占位符的描述（从文档中提取）
2. 一组实际图片的描述（由GLM-4V视觉模型生成）

请你**仔细分析每个占位符的描述和每个图片的描述**，找出它们之间的语义对应关系，然后将占位符匹配到最合适的图片。

## 匹配原则
1. **语义相似度**：占位符描述的内容应该与图片描述的内容高度一致
2. **细节匹配**：关键元素（如形状、标注、文字、数量等）必须匹配
3. **一一对应**：每个占位符匹配一个唯一的图片，**每个图片只能匹配一个占位符**
4. **不存在重复匹配**：
   - 如果多个占位符看起来相似，说明PDF识别时产生了重复
   - 在这种情况下，**只选择第一个最合适的匹配**，其他的占位符标记为null
   - 或者：选择语义最匹配的那个占位符，其他的标记为null
   - **绝对不要将同一个图片匹配给多个占位符**
5. **精确匹配**：如果找不到合适的匹配，就返回null，不要强行匹配

## 输入数据

### 占位符列表：
"""

        # 添加占位符
        for p in placeholders:
            idx = p.get('index', '?')
            ptype = p.get('type', '未知类型')
            desc = p.get('description', '')
            prompt += f"\n**占位符 {idx}**\n"
            prompt += f"- 类型: {ptype}\n"
            prompt += f"- 描述: {desc}\n"

        prompt += "\n\n### 图片描述列表：\n"

        # 添加图片描述
        for img in image_descriptions:
            filename = img.get('filename', 'unknown')
            desc = img.get('description', '')
            prompt += f"\n**{filename}**\n"
            prompt += f"- 描述: {desc}\n"

        prompt += """

## 输出格式

请严格按照以下JSON格式输出（不要输出其他内容）：

```json
{
  "matches": [
    {
      "placeholder_index": 0,
      "image_filename": "image5.png",
      "confidence": "高",
      "reason": "占位符描述'数轴示意图'与图片描述'水平向右延伸的数轴'完全匹配，且都提到了点P、Q、R、S及标注-a、a、1/a"
    }
  ],
  "unmatched_placeholders": [],
  "unmatched_images": []
}
```

说明：
- `placeholder_index`: 占位符的索引（从0开始）
- `image_filename`: 匹配的图片文件名
- `confidence`: 匹配置信度（高/中/低）
- `reason`: 匹配理由（简短说明）
- `unmatched_placeholders`: 未匹配到的占位符索引列表
- `unmatched_images`: 未匹配到的图片文件名列表

⚠️ **重要提醒**：
- **绝对不要将同一个图片文件匹配给多个占位符**
- 如果发现多个占位符看起来都匹配同一个图片，**只选择第一个（或最合适的）**，其他的放入 `unmatched_placeholders`
- 如果找不到匹配，将该占位符放入 `unmatched_placeholders`

现在请开始匹配：
"""

        # 调用DeepSeek API
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        # 提取content
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # 解析JSON
        import re
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content.strip()

        match_result = json.loads(json_str)

        # 转换为简单的映射格式
        mapping = {}
        for m in match_result.get("matches", []):
            idx = m.get("placeholder_index")
            filename = m.get("image_filename")
            if idx is not None and filename:
                mapping[idx] = filename

        return mapping

    def _split_document_by_placeholders(self, md_content: str, placeholders: List[Dict], max_chars: int = 64000) -> List[Dict]:
        """
        根据占位符位置拆分文档为多个部分

        Args:
            md_content: 完整的Markdown文档内容
            placeholders: 占位符列表
            max_chars: 每部分最大字符数（默认64k）

        Returns:
            文档部分列表，每个部分包含:
            {
                'content': str,           # 该部分的文档内容
                'placeholder_indices': []  # 该部分包含的占位符索引
            }
        """
        import re

        # 如果文档长度不超过阈值，不需要拆分
        if len(md_content) <= max_chars:
            return [{
                'content': md_content,
                'placeholder_indices': list(range(len(placeholders)))
            }]

        # 需要拆分文档
        parts = []

        # 找到所有占位符的位置
        pattern = r'<!--\s*IMAGE_PLACEHOLDER\s+type:\s*.+?\s*description:\s*.+?\s*-->'
        matches = list(re.finditer(pattern, md_content, re.DOTALL))

        if not matches:
            # 没有占位符，直接返回整个文档
            return [{
                'content': md_content,
                'placeholder_indices': []
            }]

        # 计算每个部分应该包含多少个占位符
        total_placeholders = len(matches)
        # 根据文档长度和字符限制估算需要的分段数
        estimated_parts = max(1, (len(md_content) + max_chars - 1) // max_chars)
        placeholders_per_part = max(1, (total_placeholders + estimated_parts - 1) // estimated_parts)

        # 按占位符数量拆分
        for i in range(0, total_placeholders, placeholders_per_part):
            end_idx = min(i + placeholders_per_part, total_placeholders)

            # 确定该部分的起始和结束位置
            start_pos = matches[i].start()
            if end_idx < total_placeholders:
                # 结束位置是下一个占位符之前，留一些上下文
                end_pos = matches[end_idx].start()
            else:
                # 最后一个部分，包含到文档结尾
                end_pos = len(md_content)

            # 提取该部分的内容
            part_content = md_content[start_pos:end_pos]

            # 记录该部分包含的占位符索引
            part_placeholder_indices = list(range(i, end_idx))

            parts.append({
                'content': part_content,
                'placeholder_indices': part_placeholder_indices
            })

        logger.info(f"  文档长度 {len(md_content)} 字符，拆分为 {len(parts)} 个部分")

        return parts

    def _call_deepseek_for_matching_global(self, md_content: str, placeholders: List[Dict], image_descriptions: List[Dict]) -> Dict[int, str]:
        """
        调用DeepSeek API进行语义匹配（全局上下文模式，支持文档拆分）

        Args:
            md_content: 完整的Markdown文档内容（包含占位符）
            placeholders: 占位符列表
            image_descriptions: 图片描述列表

        Returns:
            匹配映射: {placeholder_index: image_filename}
        """
        # 拆分文档（如果太长）
        MAX_DOC_CHARS = 64000  # 64k字符阈值
        doc_parts = self._split_document_by_placeholders(md_content, placeholders, MAX_DOC_CHARS)

        # 如果只有一个部分，直接处理
        if len(doc_parts) == 1:
            logger.info(f"  文档长度 {len(md_content)} 字符，无需拆分")
            return self._match_single_part(
                doc_parts[0]['content'],
                placeholders,
                image_descriptions,
                list(range(len(placeholders)))
            )

        # 多个部分：分别匹配后合并
        logger.info(f"  使用分段匹配策略：{len(doc_parts)} 个部分")
        all_matches = {}

        for part_idx, part in enumerate(doc_parts, 1):
            logger.info(f"    处理第 {part_idx}/{len(doc_parts)} 部分...")

            # 提取该部分的占位符
            part_placeholder_indices = part['placeholder_indices']
            part_placeholders = [placeholders[i] for i in part_placeholder_indices]

            # 匹配该部分
            part_matches = self._match_single_part(
                part['content'],
                part_placeholders,
                image_descriptions,
                part_placeholder_indices
            )

            # 合并结果
            all_matches.update(part_matches)

            logger.info(f"    第 {part_idx} 部分匹配完成: {len(part_matches)}/{len(part_placeholders)}")

        return all_matches

    def _match_single_part(self, md_content: str, placeholders: List[Dict], image_descriptions: List[Dict], placeholder_indices: List[int]) -> Dict[int, str]:
        """
        匹配单个文档部分

        Args:
            md_content: 该部分的文档内容
            placeholders: 该部分的占位符列表
            image_descriptions: 完整的图片描述列表
            placeholder_indices: 占位符在全局的索引列表

        Returns:
            匹配映射: {placeholder_index: image_filename}
        """
        # 构建prompt - 强调利用完整文档上下文
        prompt = """你是一个智能文档处理助手，负责将图片占位符与实际图片进行语义匹配。

## 任务说明
我会给你：
1. **完整的Markdown文档内容**（包含所有占位符及其上下文）
2. 一组实际图片的描述（由GLM-4V视觉模型生成）

请你**仔细阅读整个文档，理解每个占位符在文档中的上下文（出现在哪个题目、什么位置）**，然后将占位符匹配到最合适的图片。

## 关键优势：完整上下文
你可以通过阅读完整文档来：
- 了解每个占位符出现在哪个题目中（如"第5题"、"第23题"）
- 理解占位符周围的问题描述，推断图片应该包含什么内容
- 识别相似题目之间的细微差异
- 判断某些占位符是否是PDF识别时产生的重复

## 匹配原则
1. **上下文理解**：优先根据占位符在文档中的位置和题目内容来判断
2. **语义相似度**：占位符描述的内容应该与图片描述的内容高度一致
3. **细节匹配**：关键元素（如形状、标注、文字、数量等）必须匹配
4. **一一对应**：每个占位符匹配一个唯一的图片，**每个图片只能匹配一个占位符**
5. **不存在重复匹配**：
   - 如果多个占位符看起来相似，说明PDF识别时产生了重复
   - 在这种情况下，**只选择第一个最合适的匹配**，其他的占位符标记为null
   - 或者：选择语义最匹配的那个占位符，其他的标记为null
   - **绝对不要将同一个图片匹配给多个占位符**
6. **精确匹配**：如果找不到合适的匹配，就返回null，不要强行匹配

## 完整Markdown文档

```
{0}
```

## 占位符提取信息

为了方便参考，以下是提取出的占位符列表：
""".format(md_content)  # 不再限制长度，因为已经拆分

        # 添加占位符提取信息
        for local_idx, p in enumerate(placeholders):
            global_idx = placeholder_indices[local_idx]  # 使用全局索引
            ptype = p.get('type', '未知类型')
            desc = p.get('description', '')
            prompt += f"\n**占位符 {global_idx}**\n"
            prompt += f"- 类型: {ptype}\n"
            prompt += f"- 描述: {desc[:200]}...\n"  # 截断过长的描述

        prompt += "\n\n## 图片描述列表\n"

        # 添加图片描述
        for img in image_descriptions:
            filename = img.get('filename', 'unknown')
            desc = img.get('description', '')
            prompt += f"\n**{filename}**\n"
            prompt += f"- 描述: {desc[:300]}...\n"  # 截断过长的描述

        prompt += """

## 输出要求

请严格按照以下JSON格式输出（必须输出有效的JSON，不要包含其他内容）：

```json
{
  "matches": [
    {
      "placeholder_index": 0,
      "image_filename": "image5.png",
      "confidence": "高",
      "reason": "根据文档上下文，这是第5题的数轴图，图片描述完全匹配"
    }
  ],
  "unmatched_placeholders": [1, 5],
  "unmatched_images": ["image10.png"]
}
```

说明：
- `placeholder_index`: 占位符的索引（从0开始）
- `image_filename`: 匹配的图片文件名
- `confidence`: 匹配置信度（高/中/低）
- `reason`: 匹配理由（简短说明，可以提到文档上下文）
- `unmatched_placeholders`: 未匹配到的占位符索引列表
- `unmatched_images`: 未匹配到的图片文件名列表

⚠️ **重要提醒**：
- **绝对不要将同一个图片文件匹配给多个占位符**
- 如果发现多个占位符看起来都匹配同一个图片，**只选择第一个（或最合适的）**，其他的放入 `unmatched_placeholders`
- 如果找不到匹配，将该占位符放入 `unmatched_placeholders`

现在请开始匹配：
"""

        # 调用DeepSeek API - 使用JSON Output功能
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000,
            "response_format": {
                "type": "json_object"
            }
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        # 提取content（DeepSeek JSON Output模式直接返回JSON字符串）
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # 直接解析JSON（不需要正则提取）
        try:
            match_result = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ 解析DeepSeek返回的JSON失败: {e}")
            logger.error(f"  返回内容: {content[:500]}")
            return {}

        # 转换为简单的映射格式
        mapping = {}
        for m in match_result.get("matches", []):
            idx = m.get("placeholder_index")
            filename = m.get("image_filename")
            if idx is not None and filename:
                mapping[idx] = filename

        # 记录未匹配的占位符和图片
        unmatched = match_result.get("unmatched_placeholders", [])
        if unmatched:
            logger.warning(f"  ⚠ 未匹配的占位符: {unmatched}")

        return mapping


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PDF转Markdown工具 - 智能分类版本（支持扫描件插图提取）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 处理文字PDF（Word/出版软件转换的）
  python3 %(prog)s document.pdf

  # 处理扫描件PDF（自动识别插图）
  python3 %(prog)s scanned.pdf

  # 指定输出目录
  python3 %(prog)s input.pdf -o ./my_output

  # 使用自定义API地址
  python3 %(prog)s input.pdf --glm-api http://localhost:9999

支持的PDF类型：
  • 文字PDF（Word/LaTeX等转换）：直接提取原始嵌入图片
  • 扫描件PDF：使用GLM-4.6V-Flash识别插图位置并裁剪
  • 混合型PDF：自动选择最优处理方式
        """
    )
    parser.add_argument('input_file', help='输入PDF文件路径')
    parser.add_argument('-o', '--output', default='output_pdf_to_md', help='输出目录')
    parser.add_argument('-n', '--max-pages', type=int, default=None, help='最大处理页数（用于测试）')
    parser.add_argument('--glm-api', default='http://192.168.100.110:9999', help='GLM API地址')
    parser.add_argument('--glm-key', help='GLM API密钥')
    parser.add_argument('--deepseek-key', help='DeepSeek API密钥')

    args = parser.parse_args()

    # 创建转换器
    converter = PDFToMarkdownConverter(
        output_base_dir=args.output,
        glm_api_url=args.glm_api,
        glm_api_key=args.glm_key,
        deepseek_api_key=args.deepseek_key
    )

    # 执行转换
    success, output_path, stats = converter.convert(args.input_file)

    if success:
        print(f"\n✅ 转换成功！")
        print(f"输出文件: {output_path}")
        print(f"总图片数: {stats.get('total_images', 0)}")
        print(f"匹配成功: {stats.get('matched_images', 0)}")
        print(f"总耗时: {stats.get('processing_time', 0):.2f}秒")
        sys.exit(0)
    else:
        print(f"\n❌ 转换失败: {stats.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
