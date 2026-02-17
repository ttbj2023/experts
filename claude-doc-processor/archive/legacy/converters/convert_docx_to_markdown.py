#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCX to Markdown Converter

将DOCX文件转换为Markdown格式
- 数学公式转换为LaTeX
- 图片提取到独立目录
- 图片使用相对路径引用
"""

import os
import sys
import json
import subprocess
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 添加utils目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from docx import Document
    from docx.oxml import parse_xml
except ImportError:
    print("错误: 未安装python-docx，请运行: pip install python-docx")
    sys.exit(1)

from utils.omml_converter import OMMLConverter
from utils.image_optimizer import ImageOptimizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocxToMarkdownConverter:
    """DOCX到Markdown转换器"""

    def __init__(self, output_base_dir: str = "output_docx_to_md",
                 optimize_images: bool = True,
                 image_quality: int = 85):
        """
        初始化转换器

        Args:
            output_base_dir: 输出基础目录
            optimize_images: 是否压缩图片
            image_quality: 图片压缩质量 (1-100)
        """
        self.output_base_dir = output_base_dir
        self.optimize_images = optimize_images
        self.image_quality = image_quality

        # 初始化工具
        self.omml_converter = OMMLConverter()
        self.image_optimizer = ImageOptimizer(quality=image_quality)

        # 转换统计
        self.stats = {
            'input_file': '',
            'output_dir': '',
            'total_images': 0,
            'extracted_images': 0,
            'total_formulas': 0,
            'converted_formulas': 0,
            'fallback_images': 0,
            'processing_time': 0,
            'success': False,
            'error': None
        }

    def convert(self, input_file: str) -> Tuple[bool, str, dict]:
        """
        转换DOCX文件为Markdown

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
        images_dir = os.path.join(output_dir, 'images')
        output_md = os.path.join(output_dir, 'document.md')
        meta_json = os.path.join(output_dir, 'meta.json')

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)

        logger.info(f"开始转换: {input_file}")
        logger.info(f"输出目录: {output_dir}")

        # 更新统计信息
        self.stats['input_file'] = input_file
        self.stats['output_dir'] = output_dir

        try:
            # 步骤1: 使用LibreOffice提取图片
            logger.info("步骤1: 提取图片...")
            extracted_images = self._extract_images_with_libreoffice(input_file, images_dir)
            self.stats['extracted_images'] = len(extracted_images)
            self.stats['total_images'] = len(extracted_images)
            logger.info(f"  提取了 {len(extracted_images)} 张图片")

            # 步骤2: 读取DOCX并转换为Markdown
            logger.info("步骤2: 转换文档内容...")
            markdown_content = self._convert_docx_to_markdown(input_file, images_dir)

            # 步骤2.5: 去除水印
            logger.info("步骤2.5: 去除水印...")
            markdown_content = self._remove_watermarks(markdown_content)
            logger.info(f"  水印已去除")

            # 步骤3: 保存Markdown文件
            logger.info("步骤3: 保存Markdown文件...")
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"  已保存: {output_md}")

            # 步骤4: 压缩图片（可选）
            if self.optimize_images and extracted_images:
                logger.info("步骤4: 压缩图片...")
                self.image_optimizer.reset_stats()
                opt_stats = self.image_optimizer.optimize_directory(images_dir, recursive=False)
                logger.info(f"  压缩完成，节省: {opt_stats['saved_bytes']:,} bytes")

            # 步骤5: 生成元数据
            logger.info("步骤5: 生成元数据...")
            self.stats['success'] = True
            self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()
            self.stats['omml_conversion'] = self.omml_converter.get_stats()

            with open(meta_json, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
            logger.info(f"  已保存: {meta_json}")

            logger.info("=" * 60)
            logger.info("转换成功！")
            logger.info(f"  输出文件: {output_md}")
            logger.info(f"  图片数量: {self.stats['total_images']}")
            logger.info(f"  公式总数: {self.stats['total_formulas']}")
            logger.info(f"  LaTeX转换: {self.stats['converted_formulas']}")
            logger.info(f"  降级图片: {self.stats['fallback_images']}")
            logger.info(f"  处理时间: {self.stats['processing_time']:.2f} 秒")
            logger.info("=" * 60)

            return True, output_md, self.stats

        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.stats['success'] = False
            self.stats['error'] = error_msg
            self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()

            # 保存错误信息到元数据
            try:
                with open(meta_json, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, ensure_ascii=False, indent=2)
            except:
                pass

            return False, '', self.stats

    def _extract_images_with_libreoffice(self, input_file: str, images_dir: str) -> List[str]:
        """
        使用LibreOffice将DOCX转换为HTML并提取图片

        Args:
            input_file: 输入DOCX文件
            images_dir: 图片输出目录

        Returns:
            提取的图片文件名列表
        """
        # 创建临时目录
        temp_dir = os.path.join(images_dir, '_temp')
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 使用LibreOffice转换为HTML
            logger.info(f"  使用LibreOffice转换为HTML...")

            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'html:HTML (StarWriter)',
                '--outdir', temp_dir,
                input_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                logger.warning(f"LibreOffice转换失败: {result.stderr}")
                # 降级：尝试使用python-docx直接提取图片
                return self._extract_images_with_python_docx(input_file, images_dir)

            # 查找生成的HTML文件
            html_files = list(Path(temp_dir).glob("*.html"))

            if not html_files:
                logger.warning("LibreOffice未生成HTML文件")
                shutil.rmtree(temp_dir)
                # 降级：尝试使用python-docx直接提取图片
                return self._extract_images_with_python_docx(input_file, images_dir)

            html_file = html_files[0]

            # 提取图片：LibreOffice会在HTML同目录下创建图片文件夹
            # 文件名通常为 "filename_html_files"
            base_name = html_file.stem
            image_folder_name = f"{base_name}_files"

            image_folder = os.path.join(temp_dir, image_folder_name)

            images = []
            if os.path.exists(image_folder):
                # 复制图片到目标目录
                for file in os.listdir(image_folder):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        src = os.path.join(image_folder, file)
                        dst = os.path.join(images_dir, file)
                        shutil.copy2(src, dst)
                        images.append(file)

                logger.info(f"  从HTML提取了 {len(images)} 张图片")
            else:
                logger.info(f"  HTML未包含图片文件夹，尝试使用python-docx提取")
                images = self._extract_images_with_python_docx(input_file, images_dir)

            # 清理临时目录
            shutil.rmtree(temp_dir)

            return images

        except subprocess.TimeoutExpired:
            logger.error("LibreOffice转换超时")
            shutil.rmtree(temp_dir)
            return self._extract_images_with_python_docx(input_file, images_dir)
        except Exception as e:
            logger.error(f"LibreOffice转换异常: {str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return self._extract_images_with_python_docx(input_file, images_dir)

    def _extract_images_with_python_docx(self, input_file: str, images_dir: str) -> List[str]:
        """
        使用python-docx直接提取图片

        Args:
            input_file: 输入DOCX文件
            images_dir: 图片输出目录

        Returns:
            提取的图片文件名列表
        """
        try:
            logger.info(f"  使用python-docx提取图片...")
            doc = Document(input_file)

            # 用于重命名图片计数器
            image_counter = 1
            extracted_images = []

            # 遍历文档中的所有关系（包含图片）
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    # 获取图片数据
                    image_data = rel.target_part.blob

                    # 确定图片扩展名
                    content_type = rel.target_part.content_type
                    if 'png' in content_type:
                        ext = '.png'
                    elif 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'gif' in content_type:
                        ext = '.gif'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        ext = '.png'  # 默认

                    # 生成文件名
                    image_filename = f"image{image_counter}{ext}"
                    image_path = os.path.join(images_dir, image_filename)

                    # 保存图片
                    with open(image_path, 'wb') as f:
                        f.write(image_data)

                    extracted_images.append(image_filename)
                    image_counter += 1

            logger.info(f"  提取了 {len(extracted_images)} 张图片")
            return extracted_images

        except Exception as e:
            logger.error(f"python-docx提取图片失败: {str(e)}")
            return []

    def _convert_docx_to_markdown(self, input_file: str, images_dir: str) -> str:
        """
        将DOCX内容转换为Markdown

        Args:
            input_file: 输入DOCX文件
            images_dir: 图片目录（用于相对路径）

        Returns:
            Markdown字符串
        """
        doc = Document(input_file)
        markdown_lines = []

        # 获取图片列表
        image_files = []
        if os.path.exists(images_dir):
            image_files = sorted([f for f in os.listdir(images_dir)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))])

        image_index = 0

        for para in doc.paragraphs:
            # 跳过空段落
            if not para.text.strip() and not para._element.xpath('.//pic:pic'):
                continue

            # 检查段落中是否包含图片
            if para._element.xpath('.//pic:pic'):
                # 处理图片
                if image_index < len(image_files):
                    image_file = image_files[image_index]
                    markdown_lines.append(f"\n![{image_file}](images/{image_file})\n")
                    image_index += 1
                    self.stats['total_images'] += 1
                else:
                    logger.warning(f"图片数量超出预期，跳过第 {image_index + 1} 张图片")
                    image_index += 1

            # 检查是否包含数学公式（OMML）
            elif para._element.xpath('.//m:oMath'):
                # 处理数学公式
                self.stats['total_formulas'] += 1

                # 提取OMML XML
                omath_elements = para._element.xpath('.//m:oMath',
                                                   namespaces={'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math'})

                if omath_elements:
                    omml_xml = self._element_to_string(omath_elements[0])

                    # 转换为LaTeX
                    success, latex = self.omml_converter.omml_to_latex(omml_xml)

                    if success and latex:
                        # 使用LaTeX公式
                        # 判断是行内还是块级（简单判断：如果段落只有公式，用块级）
                        if len(para.text.strip()) == len(omath_elements[0].text or ''):
                            markdown_lines.append(f"\n$$\n{latex}\n$$\n")
                        else:
                            markdown_lines.append(f"${latex}$")
                        self.stats['converted_formulas'] += 1
                    else:
                        # 转换失败，保留为图片
                        logger.warning(f"公式转换失败，保留为图片")
                        self.stats['fallback_images'] += 1
                        if image_index < len(image_files):
                            image_file = image_files[image_index]
                            markdown_lines.append(f"\n![公式](images/{image_file})\n")
                            image_index += 1

            # 处理普通文本
            elif para.text.strip():
                text = para.text.strip()

                # 处理标题
                if para.style.name.startswith('Heading'):
                    level = para.style.name.replace('Heading ', '')
                    try:
                        level = int(level)
                        markdown_lines.append(f"\n{'#' * level} {text}\n")
                    except ValueError:
                        markdown_lines.append(f"\n{text}\n")
                else:
                    # 普通段落
                    markdown_lines.append(f"\n{text}\n")

        # 处理表格
        for table in doc.tables:
            markdown_lines.append("\n" + self._convert_table_to_markdown(table) + "\n")

        return '\n'.join(markdown_lines)

    def _convert_table_to_markdown(self, table) -> str:
        """
        将表格转换为Markdown表格格式

        Args:
            table: python-docx表格对象

        Returns:
            Markdown表格字符串
        """
        markdown_lines = []

        # 表头
        header_cells = table.rows[0].cells
        header = "| " + " | ".join(cell.text.strip() for cell in header_cells) + " |"
        separator = "|" + "|".join(["---" for _ in header_cells]) + "|"

        markdown_lines.append(header)
        markdown_lines.append(separator)

        # 表格数据
        for row in table.rows[1:]:
            cells = row.cells
            row_text = "| " + " | ".join(cell.text.strip() for cell in cells) + " |"
            markdown_lines.append(row_text)

        return '\n'.join(markdown_lines)

    def _remove_watermarks(self, text: str) -> str:
        """
        去除水印信息

        Args:
            text: 原始文本

        Returns:
            去除水印后的文本
        """
        import re

        # 去除常见的水印模式
        watermark_patterns = [
            r'声明：试题解析著作权属菁优网所有[^\n]*',  # 菁优网水印
            r'声明：试题解析著作权属[^\n]*',  # 通用著作权声明
            r'未经书面同意，不得复制发布[^\n]*',  # 版权声明
            r'发布日期：[^\n]*；用户：[^\n]*；邮箱：[^\n]*；学号：[^\n]*',  # 用户信息
            r'用户：[^\n]*；邮箱：[^\n]*；学号：[^\n]*',  # 用户信息简化版
        ]

        for pattern in watermark_patterns:
            text = re.sub(pattern, '', text)

        # 去除连续的空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        return text.strip()

    def _element_to_string(self, element) -> str:
        """
        将XML元素转换为字符串

        Args:
            element: lxml元素对象

        Returns:
            XML字符串
        """
        try:
            from lxml.etree import tostring
            return tostring(element, encoding='unicode')
        except ImportError:
            # 降级方案：使用ElementTree
            import xml.etree.ElementTree as ET
            return ET.tostring(element, encoding='unicode')


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='将DOCX文件转换为Markdown格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换单个文件
  python3 convert_docx_to_markdown.py input.docx

  # 指定输出目录
  python3 convert_docx_to_markdown.py input.docx -o output_dir

  # 不压缩图片
  python3 convert_docx_to_markdown.py input.docx --no-optimize

  # 指定图片质量
  python3 convert_docx_to_markdown.py input.docx --quality 90
        """
    )

    parser.add_argument('input_file', help='输入DOCX文件路径')
    parser.add_argument('-o', '--output', default='output_docx_to_md',
                       help='输出基础目录 (默认: output_docx_to_md)')
    parser.add_argument('--no-optimize', action='store_true',
                       help='不压缩图片')
    parser.add_argument('--quality', type=int, default=85,
                       choices=range(1, 101),
                       help='图片压缩质量 1-100 (默认: 85)')

    args = parser.parse_args()

    # 创建转换器
    converter = DocxToMarkdownConverter(
        output_base_dir=args.output,
        optimize_images=not args.no_optimize,
        image_quality=args.quality
    )

    # 执行转换
    success, output_path, stats = converter.convert(args.input_file)

    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
