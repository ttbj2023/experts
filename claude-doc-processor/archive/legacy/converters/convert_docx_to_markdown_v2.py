#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCX to Markdown Converter v2 - 图片占位符版本（通用文档）

适用范围：
- 数学、物理、化学、工程等科技文档
- 教材、论文、技术手册、报告等
- 任何包含复杂格式（公式、图表、多栏布局）的文档

优化版转换流程：
1. 从 DOCX 提取图片
2. DOCX → PDF (LibreOffice)
3. PDF → MD (GLM-4.6V-Flash，生成图片占位符)
4. 智能图片处理（占位符匹配）
   - 解析占位符
   - 匹配并插入实际图片
   - 自动清理冗余图片
   - 保留图片类型标签
"""

import os
import sys
import json
import subprocess
import shutil
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

# 添加utils目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocxToMarkdownConverterV2:
    """DOCX到Markdown转换器 v2 - 优化版"""

    def __init__(self,
                 output_base_dir: str = "output_docx_to_md_v2",
                 mineru_api_url: str = "http://localhost:8001",
                 analyze_images: bool = True,
                 min_image_size: int = 100):
        """
        初始化转换器

        Args:
            output_base_dir: 输出基础目录
            mineru_api_url: MinerU服务地址
            analyze_images: 是否使用AI分析图片
            min_image_size: 最小图片尺寸（像素），小于此尺寸的图片将被过滤（默认100px）
        """
        self.output_base_dir = output_base_dir
        self.mineru_api_url = mineru_api_url
        self.analyze_images = analyze_images
        self.min_image_size = min_image_size

        # 转换统计
        self.stats = {
            'input_file': '',
            'output_dir': '',
            'pdf_conversion_success': False,
            'pdf_conversion_time': 0,
            'md_conversion_success': False,
            'md_conversion_time': 0,
            'total_images': 0,
            'filtered_small_images': 0,
            'math_formula_images': 0,
            'other_images': 0,
            'removed_images': 0,
            'processing_time': 0,
            'success': False,
            'error': None
        }

    def convert(self, input_file: str) -> Tuple[bool, str, dict]:
        """
        转换DOCX文件为Markdown（优化版）

        Args:
            input_file: 输入DOCX文件路径

        Returns:
            (success, output_path, stats): 是否成功、输出路径、统计信息
        """
        start_time = datetime.now()

        # 验证输入文件
        if not os.path.exists(input_file):
            error_msg = f"输入文件不存在: {input_file}"
            logger.error(error_msg)
            return False, '', {'error': error_msg}

        if not input_file.lower().endswith('.docx'):
            error_msg = f"输入文件不是DOCX格式: {input_file}"
            logger.error(error_msg)
            return False, '', {'error': error_msg}

        # 设置输出路径
        file_name = Path(input_file).stem
        output_dir = os.path.join(self.output_base_dir, file_name)
        os.makedirs(output_dir, exist_ok=True)

        # 临时文件路径
        temp_pdf = os.path.join(output_dir, '_temp.pdf')
        temp_md = os.path.join(output_dir, '_temp.md')
        output_md = os.path.join(output_dir, 'document.md')
        meta_json = os.path.join(output_dir, 'meta.json')
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)

        logger.info(f"开始转换（优化版）: {input_file}")
        logger.info(f"输出目录: {output_dir}")

        self.stats['input_file'] = input_file
        self.stats['output_dir'] = output_dir

        try:
            # 步骤0: 从DOCX提取图片
            logger.info("=" * 60)
            logger.info("步骤0: 从DOCX提取图片")
            logger.info("=" * 60)

            docx_images, filtered_count = self._extract_images_from_docx(input_file, images_dir)
            logger.info(f"✓ 提取了{len(docx_images)}张图片")
            if filtered_count > 0:
                logger.info(f"  过滤了 {filtered_count} 张小图片 (<{self.min_image_size}px)")
            self.stats['filtered_small_images'] = filtered_count

            # 步骤1: DOCX → PDF
            logger.info("=" * 60)
            logger.info("步骤1: DOCX → PDF (LibreOffice)")
            logger.info("=" * 60)

            pdf_start = datetime.now()
            pdf_success = self._convert_docx_to_pdf(input_file, temp_pdf)
            self.stats['pdf_conversion_time'] = (datetime.now() - pdf_start).total_seconds()
            self.stats['pdf_conversion_success'] = pdf_success

            if not pdf_success:
                raise Exception("DOCX转PDF失败")

            logger.info(f"✓ PDF生成成功: {temp_pdf}")

            # 步骤2: PDF → MD (GLM-4.6V-Flash)
            logger.info("=" * 60)
            logger.info("步骤2: PDF → MD (GLM-4.6V-Flash)")
            logger.info("=" * 60)

            md_start = datetime.now()
            md_success = self._convert_pdf_to_markdown(temp_pdf, temp_md, output_dir)
            self.stats['md_conversion_time'] = (datetime.now() - md_start).total_seconds()
            self.stats['md_conversion_success'] = md_success

            if not md_success:
                raise Exception("PDF转Markdown失败")

            logger.info(f"✓ Markdown生成成功: {temp_md}")

            # 保存原始Markdown副本（用于调试）
            raw_md_path = os.path.join(output_dir, 'document_raw_with_placeholders.md')
            try:
                with open(temp_md, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                with open(raw_md_path, 'w', encoding='utf-8') as f:
                    f.write(raw_content)
                logger.info(f"✓ 已保存原始Markdown: {raw_md_path}")
            except Exception as e:
                logger.warning(f"保存原始Markdown失败: {e}")

            # 步骤3: 智能图片处理
            if self.analyze_images:
                logger.info("=" * 60)
                logger.info("步骤3: 智能图片处理（AI分析+插入）")
                logger.info("=" * 60)

                markdown_content = self._process_images_intelligently(temp_md, docx_images)
            else:
                logger.info("步骤3: 跳过AI图片分析，保留所有图片")
                # 不做分析，直接插入所有图片
                markdown_content = self._insert_images_to_markdown_from_docx(temp_md, docx_images)

            # 步骤4: 保存最终Markdown
            logger.info("=" * 60)
            logger.info("步骤4: 保存最终Markdown")
            logger.info("=" * 60)

            # 清理GLM可能误生成的代码块标记
            markdown_content = self._clean_code_blocks(markdown_content)

            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"✓ 已保存: {output_md}")

            # 清理临时文件
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
            if os.path.exists(temp_md):
                os.remove(temp_md)

            # 生成元数据
            self.stats['success'] = True
            self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()

            with open(meta_json, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)

            logger.info("=" * 60)
            logger.info("转换成功！")
            logger.info(f"  输出文件: {output_md}")
            logger.info(f"  总图片数: {self.stats['total_images']}")
            if self.stats['filtered_small_images'] > 0:
                logger.info(f"  过滤小图片: {self.stats['filtered_small_images']} 张")
            logger.info(f"  数学公式图片: {self.stats['math_formula_images']}")
            logger.info(f"  其他图片: {self.stats['other_images']}")
            logger.info(f"  已移除图片: {self.stats['removed_images']}")
            logger.info(f"  处理时间: {self.stats['processing_time']:.2f} 秒")
            logger.info("=" * 60)

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

    def _convert_docx_to_pdf(self, docx_path: str, pdf_path: str) -> bool:
        """
        使用LibreOffice将DOCX转换为PDF

        Args:
            docx_path: DOCX文件路径
            pdf_path: 输出PDF路径

        Returns:
            是否成功
        """
        try:
            output_dir = os.path.dirname(pdf_path)

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
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"LibreOffice转换失败: {result.stderr}")
                return False

            # LibreOffice会生成同名PDF文件
            expected_pdf = os.path.join(output_dir, Path(docx_path).stem + '.pdf')

            if os.path.exists(expected_pdf):
                if expected_pdf != pdf_path:
                    shutil.move(expected_pdf, pdf_path)
                logger.info(f"PDF文件已生成: {pdf_path}")
                return True
            else:
                logger.error(f"PDF文件未生成: {expected_pdf}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("LibreOffice转换超时")
            return False
        except Exception as e:
            logger.error(f"DOCX转PDF异常: {str(e)}")
            return False

    def _convert_pdf_to_markdown(self, pdf_path: str, md_path: str, output_dir: str) -> bool:
        """
        使用GLM-4.6V-Flash将PDF转换为Markdown（不含图片）

        Args:
            pdf_path: PDF文件路径
            md_path: 输出Markdown路径
            output_dir: 输出目录

        Returns:
            是否成功
        """
        try:
            # 导入GLM-4.6V处理器
            sys.path.insert(0, os.path.dirname(__file__))
            from process_pdf_with_glm46v_v2 import GLM46VProcessor

            # 创建处理器
            processor = GLM46VProcessor()

            # 处理PDF
            logger.info(f"调用GLM-4.6V-Flash处理PDF: {pdf_path}")

            result_path = processor.process_pdf(
                pdf_path=pdf_path,
                output_dir=output_dir,
                max_pages=None,  # 处理所有页面
                start_page=1
            )

            # 检查返回的是文件还是目录
            if result_path and os.path.isfile(result_path):
                # 返回的是full markdown文件
                if result_path != md_path:
                    shutil.move(result_path, md_path)
                logger.info(f"Markdown文件已生成: {md_path}")
                return True
            elif result_path and os.path.isdir(result_path):
                # 返回的是目录，需要手动合并page文件
                logger.info(f"GLM返回目录路径，手动合并page文件...")
                page_files = sorted([f for f in os.listdir(result_path) if f.startswith('page_') and f.endswith('.md')])

                if page_files:
                    # 合并所有page文件
                    combined_content = ""
                    for page_file in page_files:
                        page_path = os.path.join(result_path, page_file)
                        with open(page_path, 'r', encoding='utf-8') as f:
                            combined_content += f.read() + "\n\n"

                    # 保存到目标位置
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(combined_content)

                    logger.info(f"Markdown文件已生成并合并: {md_path} ({len(page_files)} 页)")
                    return True
                else:
                    logger.error("未找到page文件")
                    return False
            else:
                logger.error("GLM-4.6V-Flash未生成有效输出")
                return False

        except ImportError as e:
            logger.error(f"无法导入GLM-4.6V处理器: {str(e)}")
            logger.error("请确保 process_pdf_with_glm46v_v2.py 存在")
            return False
        except Exception as e:
            logger.error(f"PDF转Markdown异常: {str(e)}")
            return False

    def _process_images_intelligently(self, md_path: str, docx_images: List[Dict]) -> str:
        """
        智能处理图片：解析占位符并匹配实际图片

        Args:
            md_path: Markdown文件路径
            docx_images: 从DOCX提取的图片列表

        Returns:
            处理后的Markdown内容
        """
        # 读取Markdown文件
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.stats['total_images'] = len(docx_images)

        if len(docx_images) == 0:
            logger.info("DOCX中没有找到图片")
            return content

        # 解析Markdown中的图片占位符
        import re
        placeholder_pattern = r'<!--\s*IMAGE_PLACEHOLDER\s*type:\s*(.+?)\s*description:\s*(.+?)\s*-->'
        placeholders = list(re.finditer(placeholder_pattern, content, re.DOTALL))

        logger.info(f"在Markdown中找到 {len(placeholders)} 个图片占位符")
        logger.info(f"从DOCX提取了 {len(docx_images)} 张图片")

        if len(placeholders) == 0:
            logger.warning("⚠️  未找到图片占位符！")
            logger.warning("   这可能意味着：")
            logger.warning("   1. GLM模型未正确生成占位符")
            logger.warning("   2. 使用了旧版本的提示词")
            logger.warning("   请检查 process_pdf_with_glm46v_v2.py 中的提示词版本（应该是v4）")
            logger.warning("   将保留所有图片到文档末尾...")
            # 保留所有图片到文档末尾
            return self._insert_images_to_markdown_from_docx(content, docx_images)

        # 使用占位符匹配逻辑
        logger.info("✓ 使用占位符匹配模式...")
        return self._replace_placeholders_with_images(content, placeholders, docx_images)

    def _replace_placeholders_with_images(self, content: str, placeholders: list, docx_images: List[Dict]) -> str:
        """
        用实际图片替换占位符（使用GLM-4V智能匹配）

        Args:
            content: Markdown内容
            placeholders: 正则匹配的占位符列表
            docx_images: 从DOCX提取的图片列表

        Returns:
            替换后的Markdown内容
        """
        logger.info("=" * 60)
        logger.info("图片占位符智能匹配（GLM-4V）")
        logger.info("=" * 60)

        # 统计
        matched_count = 0
        unmatched_count = 0

        # 1. 准备占位符数据（提取类型和描述）
        placeholder_data = []
        for idx, placeholder in enumerate(placeholders):
            img_type = placeholder.group(1).strip()
            img_desc = placeholder.group(2).strip()
            placeholder_data.append((idx, img_type, img_desc))

        logger.info(f"📋 占位符总数: {len(placeholder_data)}")

        # 2. 准备图片数据
        image_data = []
        for idx, img_info in enumerate(docx_images):
            image_data.append((
                idx,
                img_info['filename'],
                img_info['path']
            ))

        logger.info(f"📷 图片总数: {len(image_data)}")

        # 如果没有占位符或没有图片，直接返回
        if not placeholder_data:
            logger.warning("⚠️  没有占位符需要处理")
            return content

        if not image_data:
            logger.warning("⚠️  没有图片可用于匹配")
            # 保留所有占位符
            return content

        # 3. 调用GLM进行智能匹配
        logger.info("\n🤖 启动GLM-4V智能匹配...")
        matching_results = self._match_images_with_glm_batch(placeholder_data, image_data)

        # 4. 根据匹配结果替换占位符
        used_images = set()
        unused_images_indices = set(range(len(docx_images)))

        # 从后往前替换，避免位置偏移
        for placeholder_idx in sorted(matching_results.keys(), reverse=True):
            placeholder = placeholders[placeholder_idx]
            placeholder_text = placeholder.group(0)
            img_type = placeholder.group(1).strip()
            img_desc = placeholder.group(2).strip()

            # 获取匹配的图片文件名
            matched_filename = matching_results[placeholder_idx]

            # 找到对应的图片信息
            matched_image_info = None
            matched_image_index = None
            for idx, img_info in enumerate(docx_images):
                if img_info['filename'] == matched_filename:
                    matched_image_info = img_info
                    matched_image_index = idx
                    break

            if matched_image_info:
                # 生成图片Markdown引用
                img_ref = f"\n![{img_type}](images/{matched_filename})\n"

                # 替换占位符
                content = content[:placeholder.start()] + img_ref + content[placeholder.end():]

                logger.info(f"✓ 占位符 {placeholder_idx}: {img_type[:30]}...")
                logger.info(f"  描述: {img_desc[:80]}...")
                logger.info(f"  → 匹配图片: {matched_filename}")
                logger.info(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                matched_count += 1
                used_images.add(matched_image_index)
                unused_images_indices.discard(matched_image_index)
            else:
                logger.warning(f"✗ 占位符 {placeholder_idx}: 匹配失败（图片 {matched_filename} 未找到）")
                unmatched_count += 1

        # 处理未匹配的占位符
        total_placeholders = len(placeholders)
        unmatched_placeholders = total_placeholders - len(matching_results)
        if unmatched_placeholders > 0:
            logger.warning(f"\n⚠️  {unmatched_placeholders} 个占位符未匹配，保留原样")

        # 处理未使用的图片
        unused_images = [docx_images[i] for i in unused_images_indices]
        if unused_images:
            logger.info(f"\n🗑️  未匹配的图片: {len(unused_images)} 张，准备删除...")
            # 直接删除未使用的图片文件
            for img in unused_images:
                try:
                    os.remove(img['path'])
                    logger.info(f"  ✓ 删除: {img['filename']}")
                except Exception as e:
                    logger.warning(f"  ⚠️  删除失败 {img['filename']}: {e}")

        # 更新统计
        self.stats['math_formula_images'] = 0  # 占位符模式下公式已转为LaTeX
        self.stats['other_images'] = matched_count
        self.stats['removed_images'] = len(unused_images)

        logger.info("\n" + "=" * 60)
        logger.info(f"✅ 替换完成: {matched_count} 成功, {unmatched_placeholders} 未匹配")
        logger.info(f"🗑️  删除图片: {len(unused_images)} 张")
        logger.info("=" * 60)

        return content

    def _insert_images_to_markdown_from_docx(self, content: str, images: list) -> str:
        """
        将DOCX提取的图片插入到Markdown中

        由于DOCX没有精确的页码信息，使用智能策略插入图片：
        1. 识别题目编号（如 "1.", "2.", "(1)", "(2)" 等）
        2. 在题目编号后插入图片

        Args:
            content: Markdown内容
            images: 要插入的图片信息列表（按index排序）

        Returns:
            插入图片后的Markdown内容
        """
        if not images:
            return content

        logger.info(f"将{len(images)}张图片插入到Markdown中...")

        # 按index排序
        images = sorted(images, key=lambda x: x['index'])

        # 构建图片引用列表
        image_refs = []
        for img in images:
            image_refs.append(f"\n![{img['filename']}](images/{img['filename']})\n")

        # 策略：在内容末尾添加所有图片
        # 这样做是因为：
        # 1. DOCX图片缺少精确位置信息
        # 2. GLM-4.6V-Flash已将公式转为LaTeX，剩余图片是几何图形/示意图
        # 3. 添加在末尾比随机插入更合理

        # 检查内容是否以图片结尾
        if content.rstrip().endswith('png') or content.rstrip().endswith('jpg'):
            # 已经有图片，直接追加
            content = content.rstrip() + '\n' + ''.join(image_refs)
        else:
            # 没有图片，添加分隔线后插入
            content = content.rstrip() + '\n\n' + '-' * 60 + '\n\n'
            content += '## 图片\n\n'
            content += ''.join(image_refs)

        logger.info(f"✓ 已插入{len(images)}张图片到文档末尾")

        return content

    def _insert_images_to_markdown(self, content: str, images: list) -> str:
        """
        将图片插入到Markdown的对应位置

        Args:
            content: Markdown内容
            images: 要插入的图片信息列表

        Returns:
            插入图片后的Markdown内容
        """
        if not images:
            return content

        # 按页码分组
        from collections import defaultdict
        images_by_page = defaultdict(list)
        for img in images:
            images_by_page[img['page']].append(img)

        logger.info(f"将{len(images)}张图片插入到Markdown中...")

        # 按页码顺序处理
        for page_num in sorted(images_by_page.keys()):
            page_images = images_by_page[page_num]

            # 找到对应的页面标记
            page_marker = f"## 第 {page_num} 页"

            if page_marker not in content:
                logger.warning(f"未找到页面标记: {page_marker}")
                continue

            # 在页面标记后插入图片
            insert_position = content.find(page_marker) + len(page_marker)

            # 构建图片引用
            image_refs = []
            for img in sorted(page_images, key=lambda x: x['global_index']):
                image_refs.append(f"\n![{img['filename']}]](images/{img['filename']})\n")

            # 插入图片
            content = content[:insert_position] + ''.join(image_refs) + content[insert_position:]

            logger.info(f"  页{page_num}: 插入了{len(page_images)}张图片")

        return content

    def _extract_images_from_docx(self, docx_path: str, images_dir: str) -> Tuple[List[Dict], int]:
        """
        从DOCX中直接提取图片，保持原始顺序

        Args:
            docx_path: DOCX文件路径
            images_dir: 图片输出目录

        Returns:
            (图片信息列表, 过滤的小图片数量):
            图片信息列表: [{
                'index': 序号,
                'filename': 文件名,
                'path': 文件路径,
                'width': 宽度,
                'height': 高度,
                'page': 页码（None，需要后续匹配）
            }]
            过滤数量: 整数
        """
        from docx import Document
        from docx.oxml import parse_xml
        from PIL import Image
        from io import BytesIO

        logger.info(f"从DOCX提取图片: {docx_path}")
        logger.info(f"最小尺寸阈值: {self.min_image_size}px")

        try:
            doc = Document(docx_path)
            extracted_images = []
            image_counter = 1
            filtered_count = 0

            # 遍历文档的所有关系（rels）来提取图片
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    try:
                        # 获取图片数据
                        image_data = rel.target_part.blob
                        content_type = rel.target_part.content_type

                        # 检查图片尺寸
                        img = Image.open(BytesIO(image_data))
                        width, height = img.size

                        # 过滤太小的图片
                        if width < self.min_image_size or height < self.min_image_size:
                            filtered_count += 1
                            logger.info(f"  ⊗ 过滤小图片: {width}x{height}px < {self.min_image_size}px")
                            continue

                        # 根据content_type确定扩展名
                        if 'png' in content_type:
                            ext = '.png'
                        elif 'jpeg' in content_type or 'jpg' in content_type:
                            ext = '.jpg'
                        elif 'gif' in content_type:
                            ext = '.gif'
                        elif 'bmp' in content_type:
                            ext = '.bmp'
                        else:
                            ext = '.png'

                        # 生成连续的文件名（只在确定要保存图片时才递增计数器）
                        filename = f"image{image_counter}{ext}"
                        image_path = os.path.join(images_dir, filename)

                        # 保存图片
                        with open(image_path, 'wb') as f:
                            f.write(image_data)

                        logger.info(f"  ✓ 提取图片 {image_counter}: {filename} ({width}x{height}px, {content_type})")

                        extracted_images.append({
                            'index': image_counter,
                            'filename': filename,
                            'path': image_path,
                            'width': width,
                            'height': height,
                            'page': None  # 页码需要后续匹配PDF来确定
                        })

                        image_counter += 1

                    except Exception as e:
                        logger.warning(f"  提取图片失败: {str(e)}")
                        continue

            logger.info(f"✓ 从DOCX提取了 {len(extracted_images)} 张图片")
            if filtered_count > 0:
                logger.info(f"  过滤了 {filtered_count} 张小图片 (<{self.min_image_size}px)")
            return extracted_images, filtered_count

        except ImportError:
            logger.error("无法导入python-docx库，请安装: pip install python-docx")
            return [], 0
        except Exception as e:
            logger.error(f"从DOCX提取图片失败: {str(e)}")
            return [], 0

    def _compress_image_for_glm(self, image_path: str) -> bytes:
        """
        压缩图片用于GLM-4V输入

        Args:
            image_path: 图片路径

        Returns:
            压缩后的图片数据（JPEG格式）
        """
        from PIL import Image
        from io import BytesIO

        try:
            img = Image.open(image_path)

            # 计算新尺寸（最大边长1024px）
            max_size = 1024
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # 转换为RGB（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 压缩为JPEG
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            compressed_data = buffer.getvalue()

            logger.debug(f"  图片压缩: {os.path.basename(image_path)} {len(compressed_data)/1024:.1f}KB")

            return compressed_data

        except Exception as e:
            logger.error(f"压缩图片失败 {image_path}: {e}")
            # 降级：读取原始数据
            with open(image_path, 'rb') as f:
                return f.read()

    def _call_glm_for_matching(self, placeholders: list, images: list, batch_offset: int = 0) -> tuple:
        """
        调用本地GLM-4V模型进行智能图片匹配

        将占位符描述和图片提交给GLM-4V，让模型进行语义匹配。
        约束条件：一对一匹配（每个占位符最多匹配一张图，每张图最多匹配一个占位符）。

        Args:
            placeholders: 占位符列表，格式：[(index, type, description), ...]
            images: 图片信息列表，格式：[(index, filename, filepath), ...]
            batch_offset: 批次偏移量（用于日志）

        Returns:
            (匹配结果字典, 是否需要重试)
            - 匹配结果字典：{placeholder_idx: image_filename}
            - 需要重试：True表示遇到400错误（图片太多），需要分批重试
        """
        import json
        import base64
        import requests
        from io import BytesIO

        logger.info(f"📤 调用GLM-4V进行智能匹配（批次 {batch_offset + 1}）")
        logger.info(f"   - 占位符数量: {len(placeholders)}")
        logger.info(f"   - 图片数量: {len(images)}")

        # 构建prompt
        prompt_parts = [
            "你是一个专业的文档图片匹配专家。你的任务是将**占位符描述**与**实际图片**进行精准匹配。\n",
            "## 匹配规则\n",
            "1. **一对一约束**：\n",
            "   - 每个占位符最多匹配一张图片\n",
            "   - 每张图片最多匹配一个占位符\n",
            "   - 宁可不匹配，也不要强行匹配\n",
            "2. **匹配依据**：\n",
            "   - 图片的**视觉内容**（图形、图表、示意图等）\n",
            "   - 图片的**主题和用途**（函数图像、几何图形、统计图等）\n",
            "   - 占位符的**类型**和**描述**的语义\n",
            "3. **输出格式**：\n",
            "   必须严格按照以下JSON格式输出，不要输出任何其他内容：\n",
            "   ```json\n",
            "   {\n",
            "     \"matches\": [\n",
            "       {\"placeholder_idx\": 0, \"image_idx\": 2},\n",
            "       {\"placeholder_idx\": 1, \"image_idx\": 5}\n",
            "     ]\n",
            "   }\n",
            "   ```\n",
            "   - `placeholder_idx`: 占位符的索引（从0开始）\n",
            "   - `image_idx`: 图片的索引（从0开始）\n",
            "   - 只输出**确定匹配**的项\n",
            "\n",
            "## 占位符列表\n"
        ]

        # 添加占位符信息
        for idx, ptype, desc in placeholders:
            prompt_parts.append(f"{idx}. **类型**: {ptype} | **描述**: {desc}")

        prompt_parts.append("\n## 待匹配图片\n")
        prompt_parts.append("请仔细观察每张图片的视觉内容，将它们与上面的占位符描述进行匹配。\n")

        prompt = "".join(prompt_parts)

        # 构建消息内容（包含图片）
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]

        # 添加图片（压缩后）
        for img_idx, img_filename, img_filepath in images:
            try:
                # 压缩图片
                compressed = self._compress_image_for_glm(img_filepath)
                img_b64 = base64.b64encode(compressed).decode('utf-8')

                # 添加到消息
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}"
                    }
                })

                logger.debug(f"   ✓ 已添加图片: {img_filename} (压缩后: {len(compressed)} bytes)")

            except Exception as e:
                logger.warning(f"   ⚠️  跳过图片 {img_filename}: {e}")
                continue

        # 调用API
        api_url = "http://192.168.100.110:9999/v1/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "model": "glm-4v",
            "messages": messages,
            "temperature": 0.1,  # 低温度保证确定性
            "max_tokens": 2000
        }

        try:
            logger.info(f"🔜 正在调用API {api_url}...")
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=120
            )

            # 检查响应状态码
            logger.debug(f"   HTTP状态码: {response.status_code}")

            # 检查响应体是否为空（在JSON解析之前）
            if not response.text or len(response.text.strip()) == 0:
                logger.warning(f"⚠️  API返回空响应（可能图片太多，需要分批）")
                return {}, True  # 返回空结果和重试标记

            response.raise_for_status()

            # 尝试解析JSON
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                # JSON解析失败，很可能是图片太多导致的
                logger.warning(f"⚠️  JSON解析失败（响应体不是有效JSON，可能图片太多）")
                logger.debug(f"   响应内容前500字符: {response.text[:500]}")
                return {}, True  # 返回空结果和重试标记

            # 解析响应
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # 检查content是否为空
            if not content or len(content.strip()) == 0:
                logger.warning(f"⚠️  API返回空content字段（可能图片太多）")
                return {}, True  # 返回空结果和重试标记

            logger.debug(f"📥 GLM响应:\n{content}")

            # 提取JSON（可能被包裹在代码块中）
            import re
            json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = content.strip()

            # 解析匹配结果
            match_data = json.loads(json_str)
            matches = match_data.get("matches", [])

            # 转换为字典格式：{placeholder_idx: image_filename}
            result_map = {}
            used_images = set()

            for match in matches:
                p_idx = match.get("placeholder_idx")
                i_idx = match.get("image_idx")

                if p_idx is None or i_idx is None:
                    continue

                # 检查索引范围
                if p_idx >= len(placeholders) or i_idx >= len(images):
                    logger.warning(f"   ⚠️  匹配结果超出范围: placeholder_idx={p_idx}, image_idx={i_idx}")
                    continue

                # 一对一约束检查
                if i_idx in used_images:
                    logger.warning(f"   ⚠️  图片 {i_idx} 被重复匹配，跳过")
                    continue

                result_map[p_idx] = images[i_idx][1]  # 存储文件名
                used_images.add(i_idx)

            logger.info(f"✅ 匹配完成: {len(result_map)}/{len(placeholders)} 个占位符成功匹配")

            return result_map, False  # 成功，不需要重试

        except requests.exceptions.HTTPError as e:
            # 检查是否是400错误（图片太多）
            if e.response.status_code == 400:
                logger.warning(f"⚠️  图片太多导致400错误，需要分批处理")
                return {}, True  # 返回空结果和重试标记
            else:
                logger.error(f"❌ HTTP错误: {e}")
                return {}, False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API调用失败: {e}")
            return {}, False
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}")
            logger.error(f"   响应内容: {content[:500]}")
            return {}, False
        except Exception as e:
            logger.error(f"❌ 匹配过程出错: {e}")
            return {}, False

    def _match_images_with_glm_batch(self, placeholders: list, docx_images: list) -> dict:
        """
        使用GLM-4V进行智能图片匹配（支持分批处理）

        采用自适应批处理策略：
        1. 首先尝试一次性匹配所有图片
        2. 如果遇到400错误（图片太多），分2批处理
        3. 如果仍遇到400错误，分4批处理
        4. 严格执行一对一匹配约束

        Args:
            placeholders: 占位符列表，格式：[(index, type, description), ...]
            docx_images: 图片信息列表，格式：[(index, filename, filepath), ...]

        Returns:
            匹配结果字典：{placeholder_idx: image_filename}
        """
        import math

        total_placeholders = len(placeholders)
        total_images = len(docx_images)

        logger.info(f"🎯 开始GLM智能匹配")
        logger.info(f"   - 占位符总数: {total_placeholders}")
        logger.info(f"   - 图片总数: {total_images}")

        # 最终匹配结果
        final_matches = {}
        used_image_indices = set()

        # 未匹配的占位符和图片
        unmatched_placeholders = placeholders.copy()
        unmatched_images = docx_images.copy()

        # 尝试不同的批次策略
        batch_strategies = [1, 2, 4]  # 1批、2批、4批

        for strategy_idx, num_batches in enumerate(batch_strategies):
            if not unmatched_placeholders or not unmatched_images:
                break

            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 策略 {strategy_idx + 1}: 分 {num_batches} 批处理")
            logger.info(f"{'='*60}")

            # 计算每批的占位符和图片数量
            placeholders_per_batch = math.ceil(len(unmatched_placeholders) / num_batches)
            images_per_batch = math.ceil(len(unmatched_images) / num_batches)

            # 标记：是否需要增加批次数（遇到400错误）
            need_more_batches = False

            # 逐批处理
            for batch_idx in range(num_batches):
                if not unmatched_placeholders or not unmatched_images:
                    break

                # 计算当前批次范围
                p_start = batch_idx * placeholders_per_batch
                p_end = min(p_start + placeholders_per_batch, len(unmatched_placeholders))
                i_start = batch_idx * images_per_batch
                i_end = min(i_start + images_per_batch, len(unmatched_images))

                # 当前批次的占位符和图片
                batch_placeholders = unmatched_placeholders[p_start:p_end]
                batch_images = unmatched_images[i_start:i_end]

                if not batch_placeholders or not batch_images:
                    continue

                logger.info(f"\n📦 批次 {batch_idx + 1}/{num_batches}")
                logger.info(f"   - 占位符: {len(batch_placeholders)} (索引 {p_start}-{p_end-1})")
                logger.info(f"   - 图片: {len(batch_images)} (索引 {i_start}-{i_end-1})")

                # 调用GLM进行匹配，获取结果和重试标记
                batch_matches, need_retry = self._call_glm_for_matching(
                    batch_placeholders,
                    batch_images,
                    batch_offset=batch_idx
                )

                # 如果遇到400错误，标记需要更多批次数
                if need_retry:
                    logger.warning(f"   ⚠️  本批次遇到400错误，需要增加批次数")
                    need_more_batches = True
                    break  # 退出当前批次循环，进入下一个策略

                # 处理匹配结果
                if batch_matches:
                    logger.info(f"   ✓ 本批次匹配成功: {len(batch_matches)} 个")

                    # 记录匹配关系
                    for local_p_idx, image_filename in batch_matches.items():
                        # 转换为全局索引
                        global_p_idx = p_start + local_p_idx

                        # 找到对应的图片索引
                        matched_img_idx = None
                        for i, (idx, filename, _) in enumerate(batch_images):
                            if filename == image_filename:
                                matched_img_idx = i
                                break

                        if matched_img_idx is not None and matched_img_idx not in used_image_indices:
                            final_matches[global_p_idx] = image_filename
                            used_image_indices.add(matched_img_idx)
                            logger.debug(f"      → 占位符 {global_p_idx} ↔ {image_filename}")
                else:
                    logger.warning(f"   ✗ 本批次匹配失败（无匹配结果）")
                    # 匹配失败但不一定是400错误，继续尝试

            # 如果需要更多批次数，进入下一个策略
            if need_more_batches:
                logger.info(f"🔄 当前策略失败，尝试下一策略（更多批次）...")
                continue

            # 如果成功处理完所有批次，退出循环
            if not need_more_batches:
                break

            # 过滤掉已匹配的占位符和图片
            if final_matches:
                unmatched_placeholders = [
                    (idx, ptype, desc)
                    for idx, (i, ptype, desc) in enumerate(placeholders)
                    if idx not in final_matches
                ]

                unmatched_images = [
                    (idx, filename, filepath)
                    for idx, (i, filename, filepath) in enumerate(docx_images)
                    if i not in used_image_indices
                ]

                logger.info(f"\n📊 当前进度:")
                logger.info(f"   - 已匹配: {len(final_matches)}/{total_placeholders} 占位符")
                logger.info(f"   - 未匹配: {len(unmatched_placeholders)} 占位符, {len(unmatched_images)} 图片")

                # 如果全部匹配完成，提前退出
                if len(final_matches) == total_placeholders:
                    logger.info("   ✅ 所有占位符已匹配完成！")
                    break

        # 最终报告
        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 GLM智能匹配完成")
        logger.info(f"{'='*60}")
        logger.info(f"✓ 成功匹配: {len(final_matches)}/{total_placeholders} 个占位符")
        logger.info(f"✓ 匹配率: {len(final_matches)/total_placeholders*100:.1f}%")

        if len(final_matches) < total_placeholders:
            unmatched_count = total_placeholders - len(final_matches)
            logger.warning(f"⚠️  未匹配: {unmatched_count} 个占位符")

        return final_matches

    def _clean_code_blocks(self, content: str) -> str:
        """
        清理GLM可能误生成的代码块标记

        GLM有时会错误地使用 ```markdown 或 ~~~ 包裹正文内容，
        这个函数会移除这些代码块标记，保留内部内容。

        Args:
            content: Markdown内容

        Returns:
            清理后的Markdown内容
        """
        import re

        # 移除 ```markdown ... ``` 代码块（保留内部内容）
        content = re.sub(r'```markdown\s*\n(.*?)```\n', r'\1', content, flags=re.DOTALL)

        # 移除 ``` ... ``` 代码块（保留内部内容）
        content = re.sub(r'```\s*\n(.*?)```\n', r'\1', content, flags=re.DOTALL)

        # 移除 ~~~ ... ~~~ 代码块（保留内部内容）
        content = re.sub(r'~~~\s*\n(.*?)~~~\n', r'\1', content, flags=re.DOTALL)

        # 清理多余的空行（连续超过2个空行的情况）
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

        logger.info("✓ 已清理代码块标记")

        return content

    def _remove_image_reference(self, content: str, image_file: str) -> str:
        """
        从Markdown中移除图片引用（已废弃）

        Args:
            content: Markdown内容
            image_file: 图片文件名

        Returns:
            移除图片引用后的内容
        """
        # 移除图片引用
        pattern = rf'!\[([^\]]*)\]\(images/{re.escape(image_file)}\)'
        content = re.sub(pattern, '', content)

        # 清理多余的空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='将DOCX文件转换为Markdown格式（图片占位符版本）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
优化版转换流程：
  1. 从 DOCX 提取图片
  2. DOCX → PDF (LibreOffice)
  3. PDF → MD (GLM-4.6V-Flash，生成图片占位符)
  4. 智能图片处理（占位符匹配）

示例:
  # 转换单个文件（默认使用占位符匹配）
  python3 convert_docx_to_markdown_v2.py input.docx

  # 禁用智能图片处理（保留所有图片到文档末尾）
  python3 convert_docx_to_markdown_v2.py input.docx --no-analyze
        """
    )

    parser.add_argument('input_file', help='输入DOCX文件路径')
    parser.add_argument('-o', '--output', default='output_docx_to_md_v2',
                       help='输出基础目录 (默认: output_docx_to_md_v2)')
    parser.add_argument('--no-analyze', action='store_true',
                       help='禁用智能图片处理（保留所有图片到文档末尾）')
    parser.add_argument('--min-image-size', type=int, default=100,
                       metavar='PIXELS',
                       help='最小图片尺寸（像素），小于此尺寸的图片将被过滤 (默认: 100)')

    args = parser.parse_args()

    # 创建转换器
    converter = DocxToMarkdownConverterV2(
        output_base_dir=args.output,
        analyze_images=not args.no_analyze,
        min_image_size=args.min_image_size
    )

    # 执行转换
    success, output_path, stats = converter.convert(args.input_file)

    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
