#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 到 Word 兼容 HTML 转换器
================================

将 Markdown 文件转换为 Word 100% 兼容的 HTML 文档。

核心功能：
- 解析 Markdown 结构（标题、列表、表格、公式、图片等）
- 生成符合 HTML 4.01 + CSS 2.1 标准的 HTML
- Base64 内嵌图片（无裂图问题）
- MathJax 公式支持（可编辑）
- 支持多栏布局、复杂表格、多层列表

使用示例：
```bash
./convert-md-to-html.py input.md -o output/
```

作者：Claude Code
版本：v1.0
"""

import os
import sys
from typing import Dict, Tuple
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.converters.base import BaseConverter
from src.utils.markdown_parser import MarkdownParser
from src.utils.word_html_generator import WordHTMLGenerator
from src.utils.template_loader import TemplateLoader


class MarkdownToHTMLConverter(BaseConverter):
    """Markdown 到 Word 兼容 HTML 转换器"""

    def __init__(self, config_path: str = None, template_name: str = None):
        """
        初始化转换器

        Args:
            config_path: 配置文件路径
            template_name: 模板名称（可选）
        """
        super().__init__(config_path)

        # 初始化核心组件
        self.parser = MarkdownParser()

        # 获取转换器配置
        self.converter_config = self.config.get('markdown_to_html', {})

        # 如果指定了模板，加载模板配置并合并
        if template_name:
            template_loader = TemplateLoader()
            template_config = template_loader.get_template_config_for_html_generator(template_name)

            if template_config:
                # 合并模板配置到默认配置
                self.converter_config.update(template_config)
                self.logger.info(f"已加载模板: {template_name}")
            else:
                self.logger.warning(f"模板 '{template_name}' 加载失败，使用默认配置")

        # 初始化 HTML 生成器
        self.html_generator = WordHTMLGenerator(
            config=self.converter_config
        )

        self.logger.info("MarkdownToHTMLConverter 初始化完成")

    def convert(
        self,
        input_path: str,
        output_dir: str,
        images_dir: str = None,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """
        执行 Markdown 到 HTML 的转换

        Args:
            input_path: Markdown 文件路径
            output_dir: 输出目录
            images_dir: 图片文件夹路径（默认为输出目录下的 images/）
            **kwargs: 额外参数

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self._start_timer()

        # 验证输入文件
        if not self._validate_input_file(input_path, ['.md', '.markdown']):
            return False, '', self.stats

        # 创建输出目录
        if not self._create_output_dir(output_dir):
            return False, '', self.stats

        # 确定图片目录
        if images_dir is None:
            # 默认使用输出目录下的 images/ 文件夹
            images_dir = os.path.join(output_dir, 'images')

        self.logger.info("\n" + "=" * 70)
        self.logger.info("Markdown → Word 兼容 HTML 转换流程")
        self.logger.info("=" * 70)
        self.logger.info(f"输入文件: {input_path}")
        self.logger.info(f"输出目录: {output_dir}")
        self.logger.info(f"图片目录: {images_dir}")

        try:
            # ========== Stage 1: 读取 Markdown ==========
            self.logger.info("\n[1/3] 读取 Markdown 文件...")
            with open(input_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            char_count = len(markdown_content)
            line_count = len(markdown_content.split('\n'))

            self.logger.info(f"✓ Markdown 长度: {char_count} 字符, {line_count} 行")
            self.stats['input_file'] = input_path
            self.stats['char_count'] = char_count
            self.stats['line_count'] = line_count
            self.stats['stages_completed'].append('Stage 1: 读取 Markdown')

            # ========== Stage 2: 解析 Markdown ==========
            self.logger.info("\n[2/3] 解析 Markdown 结构...")
            parsed_content = self.parser.parse(markdown_content)

            sections_count = len(parsed_content.get('sections', []))

            self.logger.info(f"✓ 解析完成: {sections_count} 个章节/元素")

            # 统计元素类型
            element_types = {}
            for section in parsed_content.get('sections', []):
                element_type = section.get('type', 'unknown')
                element_types[element_type] = element_types.get(element_type, 0) + 1

            if element_types:
                self.logger.info("  元素统计:")
                for elem_type, count in sorted(element_types.items()):
                    self.logger.info(f"    - {elem_type}: {count}")

            self.stats['sections_count'] = sections_count
            self.stats['element_types'] = element_types
            self.stats['stages_completed'].append('Stage 2: 解析 Markdown')

            # ========== Stage 3: 生成 HTML ==========
            self.logger.info("\n[3/3] 生成 Word 兼容 HTML...")

            # 获取 Markdown 文件所在目录（用于查找相对路径图片）
            md_file_dir = os.path.dirname(os.path.abspath(input_path)) if input_path else None

            html_content = self.html_generator.generate(
                parsed_content,
                images_dir=images_dir,
                md_file_dir=md_file_dir
            )

            html_length = len(html_content)

            self.logger.info(f"✓ HTML 生成完成: {html_length} 字符")
            self.stats['html_length'] = html_length
            self.stats['stages_completed'].append('Stage 3: 生成 HTML')

            # ========== 保存 HTML 文件 ==========
            output_file = self._get_output_filename(input_path, output_dir).replace('.md', '.html')

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"✅ HTML 文件已保存: {output_file}")

            # 统计信息
            self.stats['output_file'] = output_file
            self.stats['images_dir'] = images_dir
            self.stats['success'] = True

            # 保存元数据
            self._save_metadata(output_dir, self.stats)

            self._stop_timer()

            # 输出统计
            self._log_stats(self.stats)

            # 使用提示
            self.logger.info("\n" + "=" * 70)
            self.logger.info("📖 使用说明")
            self.logger.info("=" * 70)
            self.logger.info("1. 用 Microsoft Word 打开生成的 HTML 文件")
            self.logger.info(f"   文件路径: {output_file}")
            self.logger.info("2. 检查排版、公式、图片是否正常")
            self.logger.info("3. 文件 → 另存为 → 选择 .docx 格式")
            self.logger.info("4. 完成！DOCX 文件可直接编辑")
            self.logger.info("=" * 70)

            return True, output_file, self.stats

        except Exception as e:
            self.logger.error(f"❌ 转换失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

            self._stop_timer()
            self.stats['error'] = str(e)
            self.stats['success'] = False

            return False, '', self.stats

    def _get_output_filename(self, input_path: str, output_dir: str) -> str:
        """
        生成输出文件名

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录

        Returns:
            输出文件完整路径
        """
        basename = os.path.basename(input_path)
        filename = os.path.splitext(basename)[0]
        return os.path.join(output_dir, f"{filename}.html")

    def _log_stats(self, stats: Dict):
        """
        输出统计信息

        Args:
            stats: 统计信息字典
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info("转换统计")
        self.logger.info("=" * 70)
        self.logger.info(f"输入文件: {stats.get('input_file', 'N/A')}")
        self.logger.info(f"输出文件: {stats.get('output_file', 'N/A')}")
        self.logger.info(f"字符数量: {stats.get('char_count', 0):,}")
        self.logger.info(f"行数: {stats.get('line_count', 0):,}")
        self.logger.info(f"章节数量: {stats.get('sections_count', 0)}")
        self.logger.info(f"HTML 长度: {stats.get('html_length', 0):,} 字符")

        element_types = stats.get('element_types', {})
        if element_types:
            self.logger.info("\n元素类型分布:")
            for elem_type, count in sorted(element_types.items()):
                self.logger.info(f"  - {elem_type}: {count}")

        self.logger.info(f"处理时间: {stats.get('processing_time', 0):.2f} 秒")
        self.logger.info(f"状态: {'✅ 成功' if stats.get('success') else '❌ 失败'}")
        self.logger.info("=" * 70)


if __name__ == '__main__':
    # 测试代码
    import argparse

    parser = argparse.ArgumentParser(
        description='Markdown 转 Word 兼容 HTML 转换器'
    )

    parser.add_argument('input_md', help='输入 Markdown 文件')
    parser.add_argument('-o', '--output', dest='output_dir', default='output_html',
                       help='输出目录（默认: output_html）')
    parser.add_argument('--images-dir', dest='images_dir',
                       help='图片文件夹路径（默认: 输出目录/images/）')
    parser.add_argument('--config', dest='config_path',
                       help='配置文件路径')

    args = parser.parse_args()

    # 创建转换器
    converter = MarkdownToHTMLConverter(config_path=args.config_path)

    # 执行转换
    success, output_path, stats = converter.convert(
        args.input_md,
        args.output_dir,
        images_dir=args.images_dir
    )

    # 退出码
    sys.exit(0 if success else 1)
