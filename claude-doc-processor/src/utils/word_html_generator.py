#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 兼容 HTML 生成器
====================

根据 docs/HTML_support_by_WORD.md 规范，生成 Word 100% 兼容的 HTML。

核心特性：
- HTML 4.01 Transitional DOCTYPE
- CSS 2.1 兼容样式
- Base64 内嵌图片（无裂图）
- MathJax 公式支持（可编辑）
- 多栏布局、复杂表格、多层列表

作者：Claude Code
版本：v1.0
"""

import os
import re
from typing import Dict, List, Any
from .image_base64_encoder import ImageBase64Encoder


class WordHTMLGenerator:
    """Word 兼容 HTML 生成器"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化生成器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.image_encoder = ImageBase64Encoder(
            max_size=self.config.get('image_max_size', 1280),
            quality=self.config.get('image_quality', 85)
        )

        # 获取样式配置
        self.font_family = self.config.get('default_font', '宋体')
        self.font_size = self.config.get('default_font_size', 10.5)
        self.line_height = self.config.get('line_height', 1.6)

    def generate(self, parsed_content: Dict[str, Any], images_dir: str = None) -> str:
        """
        生成完整的 HTML 文档

        Args:
            parsed_content: 解析后的 Markdown 内容
            images_dir: 图片文件夹路径（用于相对路径转 base64）

        Returns:
            完整的 HTML 文档字符串
        """
        # 生成文档头部
        html_parts = [self._generate_header(parsed_content.get('metadata', {}))]

        # 生成样式
        html_parts.append(self._generate_styles())

        # 关闭 head
        html_parts.append('</head>')

        # 生成 body
        html_parts.append('<body>')

        # 生成内容
        for section in parsed_content.get('sections', []):
            html_parts.append(self._generate_section(section, images_dir))

        # 生成文档尾部
        html_parts.append('</body></html>')

        return '\n'.join(html_parts)

    def _generate_header(self, metadata: Dict[str, Any]) -> str:
        """
        生成 HTML 文档头部

        Args:
            metadata: 元数据字典

        Returns:
            HTML 头部字符串
        """
        title = metadata.get('title', '转换生成文档')

        header = f'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>{title}</title>'''

        # 添加 MathJax（如果启用）
        if self.config.get('include_mathjax', True):
            header += '''
    <script type="text/javascript" async
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>'''

        return header

    def _generate_styles(self) -> str:
        """
        生成 Word 兼容的 CSS 样式

        Returns:
            style 标签内的 CSS 内容
        """
        styles = f'''    <style type="text/css">
        /* ==================== 全局样式 ==================== */
        body {{
            font-family: '{self.font_family}', 'Times New Roman', serif;
            font-size: {self.font_size}pt;
            line-height: {self.line_height};
            margin: 0;
            padding: 20pt 30pt;
        }}

        /* ==================== 标题样式 ==================== */
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            margin: 12pt 0;
            page-break-after: avoid;
        }}

        h2 {{
            font-size: 16pt;
            font-weight: bold;
            margin: 10pt 0;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: 14pt;
            font-weight: bold;
            margin: 8pt 0;
            page-break-after: avoid;
        }}

        h4 {{
            font-size: 12pt;
            font-weight: bold;
            margin: 6pt 0;
            page-break-after: avoid;
        }}

        h5 {{
            font-size: 11pt;
            font-weight: bold;
            margin: 5pt 0;
        }}

        h6 {{
            font-size: 10pt;
            font-weight: bold;
            margin: 4pt 0;
        }}

        /* ==================== 段落样式 ==================== */
        p {{
            margin: 5pt 0;
            text-indent: 2em;
        }}

        p.no-indent {{
            text-indent: 0;
        }}

        /* ==================== 文本样式 ==================== */
        strong, b {{
            font-weight: bold;
        }}

        em, i {{
            font-style: italic;
        }}

        u {{
            text-decoration: underline;
        }}

        s {{
            text-decoration: line-through;
        }}

        sup {{
            font-size: 0.7em;
            vertical-align: super;
        }}

        sub {{
            font-size: 0.7em;
            vertical-align: sub;
        }}

        code {{
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 2pt 4pt;
        }}

        /* ==================== 列表样式 ==================== */
        ul, ol {{
            margin: 5pt 0;
            padding-left: 20pt;
        }}

        li {{
            margin: 3pt 0;
        }}

        /* 二级列表缩进 */
        ul ul, ol ol, ul ol, ol ul {{
            margin: 3pt 0 3pt 15pt;
        }}

        /* ==================== 表格样式 ==================== */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 10pt 0;
        }}

        td, th {{
            border: 1px solid #000;
            padding: 4pt;
            text-align: center;
        }}

        th {{
            font-weight: bold;
            background-color: #f0f0f0;
        }}

        /* ==================== 图片样式 ==================== */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 10pt auto;
        }}

        .figure {{
            text-align: center;
            margin: 10pt 0;
            break-inside: avoid;
        }}

        .figure-caption {{
            text-align: center;
            font-size: 9.5pt;
            margin: 5pt 0;
            text-indent: 0;
        }}

        /* ==================== 公式样式 ==================== */
        .formula-block {{
            margin: 8pt 0;
            text-align: center;
            break-inside: avoid;
        }}

        /* ==================== 代码块样式 ==================== */
        pre {{
            background-color: #f5f5f5;
            padding: 10pt;
            margin: 10pt 0;
            font-family: 'Courier New', monospace;
            white-space: pre;
            break-inside: avoid;
        }}

        /* ==================== 多栏布局 ==================== */
        .two-column {{
            column-count: 2;
            column-gap: 24pt;
            column-rule: 1pt solid #cce0f5;
            margin: 10pt 0;
        }}

        .three-column {{
            column-count: 3;
            column-gap: 20pt;
            column-rule: 1pt solid #cce0f5;
            margin: 10pt 0;
        }}

        /* ==================== 引用块样式 ==================== */
        blockquote {{
            margin: 10pt 20pt;
            padding-left: 10pt;
            border-left: 3pt solid #ccc;
            color: #666;
        }}

        /* ==================== 水平分隔线 ==================== */
        hr {{
            border: none;
            border-top: 1pt solid #ccc;
            margin: 15pt 0;
        }}

        /* ==================== 页面控制 ==================== */
        @page {{
            size: A4;
            margin: 20pt 30pt;
        }}

        /* 防止元素被拆分 */
        .no-break {{
            break-inside: avoid;
        }}
    </style>'''

        return styles

    def _generate_section(self, section: Dict[str, Any], images_dir: str = None) -> str:
        """
        生成单个章节/元素的 HTML

        Args:
            section: 章节数据
            images_dir: 图片文件夹路径

        Returns:
            HTML 字符串
        """
        element_type = section.get('type')

        if element_type == 'heading':
            return self._generate_heading(section)

        elif element_type == 'paragraph':
            return self._generate_paragraph(section, images_dir)

        elif element_type == 'list':
            return self._generate_list(section)

        elif element_type == 'table':
            return self._generate_table(section)

        elif element_type == 'code_block':
            return self._generate_code_block(section)

        elif element_type == 'hr':
            return '<hr>\n'

        elif element_type == 'blockquote':
            return self._generate_blockquote(section)

        elif element_type == 'columns':
            return self._generate_columns(section, images_dir)

        else:
            # 未知类型，返回空字符串
            return ''

    def _generate_heading(self, heading: Dict[str, Any]) -> str:
        """
        生成标题 HTML

        Args:
            heading: 标题数据

        Returns:
            HTML 字符串
        """
        level = heading.get('level', 1)
        content = heading.get('content', '')

        # 防止标题被拆分
        html = f'<div style="break-inside: avoid;">\n'
        html += f'    <h{level}>{content}</h{level}>\n'
        html += '</div>\n'

        return html

    def _generate_paragraph(self, paragraph: Dict[str, Any], images_dir: str = None) -> str:
        """
        生成段落 HTML

        Args:
            paragraph: 段落数据
            images_dir: 图片文件夹路径

        Returns:
            HTML 字符串
        """
        content = paragraph.get('content', '')
        elements = paragraph.get('elements', [])

        # 处理图片元素
        if any(e.get('type') == 'image' for e in elements):
            return self._generate_paragraph_with_image(paragraph, images_dir)

        # 处理公式元素
        if any(e.get('type') == 'formula' for e in elements):
            return self._generate_paragraph_with_formula(paragraph)

        # 普通段落
        html = f'<p>{content}</p>\n'
        return html

    def _generate_paragraph_with_image(self, paragraph: Dict[str, Any], images_dir: str = None) -> str:
        """
        生成包含图片的段落

        Args:
            paragraph: 段落数据
            images_dir: 图片文件夹路径

        Returns:
            HTML 字符串
        """
        elements = paragraph.get('elements', [])
        html = '<div class="figure">\n'

        for element in elements:
            if element.get('type') == 'image':
                image_path = element.get('path', '')
                alt_text = element.get('alt', '图片')

                # 处理图片路径
                if images_dir and not os.path.isabs(image_path):
                    full_path = os.path.join(images_dir, os.path.basename(image_path))
                else:
                    full_path = image_path

                # 转换为 base64
                try:
                    data_uri = self.image_encoder.encode_image(full_path)
                    html += f'    <img src="{data_uri}" alt="{alt_text}">\n'
                except Exception as e:
                    html += f'    <p>[图片加载失败: {alt_text}]</p>\n'

                # 添加图注
                if alt_text and alt_text != '图片':
                    html += f'    <p class="figure-caption">{alt_text}</p>\n'

        html += '</div>\n'
        return html

    def _generate_paragraph_with_formula(self, paragraph: Dict[str, Any]) -> str:
        """
        生成包含公式的段落

        Args:
            paragraph: 段落数据

        Returns:
            HTML 字符串
        """
        content = paragraph.get('content', '')
        elements = paragraph.get('elements', [])

        # 替换公式占位符为 Word 兼容的 <script> 标签
        for element in elements:
            if element.get('type') == 'formula':
                mode = element.get('mode', 'inline')
                formula = element.get('content', '')

                if mode == 'display':
                    # 块级公式
                    formula_html = f'<script type="math/tex; mode=display">{formula}</script>'
                    # 直接字符串替换（公式内容保持原样，不转义）
                    placeholder = f'{{FORMULA_DISPLAY:{formula}}}'
                    content = content.replace(placeholder, formula_html)
                else:
                    # 行内公式
                    formula_html = f'<script type="math/tex">{formula}</script>'
                    # 直接字符串替换（公式内容保持原样，不转义）
                    placeholder = f'{{FORMULA_INLINE:{formula}}}'
                    content = content.replace(placeholder, formula_html)

        html = f'<p>{content}</p>\n'
        return html

    def _generate_list(self, list_data: Dict[str, Any]) -> str:
        """
        生成列表 HTML

        Args:
            list_data: 列表数据

        Returns:
            HTML 字符串
        """
        ordered = list_data.get('ordered', False)
        items = list_data.get('items', [])
        start = list_data.get('start', 1)

        tag = 'ol' if ordered else 'ul'
        attrs = f' start="{start}"' if ordered and start > 1 else ''

        html = f'<{tag}{attrs}>\n'

        for item in items:
            if isinstance(item, dict) and 'nested_list' in item:
                # 带嵌套列表的项
                html += f'    <li>{item["content"]}\n'
                html += self._generate_nested_list(item['nested_list'])
                html += '    </li>\n'
            else:
                html += f'    <li>{item}</li>\n'

        html += f'</{tag}>\n'
        return html

    def _generate_nested_list(self, nested_list: Dict[str, Any]) -> str:
        """
        生成嵌套列表 HTML

        Args:
            nested_list: 嵌套列表数据

        Returns:
            HTML 字符串
        """
        ordered = nested_list.get('ordered', False)
        items = nested_list.get('items', [])

        tag = 'ol' if ordered else 'ul'

        html = f'<{tag}>\n'

        for item in items:
            html += f'    <li>{item}</li>\n'

        html += f'</{tag}>\n'
        return html

    def _generate_table(self, table_data: Dict[str, Any]) -> str:
        """
        生成表格 HTML

        Args:
            table_data: 表格数据

        Returns:
            HTML 字符串
        """
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])

        html = '<table border="1" cellpadding="4" cellspacing="0" width="100%">\n'

        # 表头
        if headers:
            html += '    <thead>\n'
            html += '        <tr>\n'
            for header in headers:
                html += f'            <th align="center">{header}</th>\n'
            html += '        </tr>\n'
            html += '    </thead>\n'

        # 表体
        html += '    <tbody>\n'
        for row in rows:
            html += '        <tr>\n'
            for cell in row:
                content = cell.get('content', '')
                html += f'            <td align="center">{content}</td>\n'
            html += '        </tr>\n'
        html += '    </tbody>\n'

        html += '</table>\n'
        return html

    def _generate_code_block(self, code_data: Dict[str, Any]) -> str:
        """
        生成代码块 HTML

        Args:
            code_data: 代码块数据

        Returns:
            HTML 字符串
        """
        code = code_data.get('content', '')
        language = code_data.get('language', 'text')

        # 转义 HTML 特殊字符
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        html = '<pre>'
        html += code
        html += '</pre>\n'

        return html

    def _generate_blockquote(self, quote_data: Dict[str, Any]) -> str:
        """
        生成引用块 HTML

        Args:
            quote_data: 引用块数据

        Returns:
            HTML 字符串
        """
        content = quote_data.get('content', '')

        html = f'<blockquote>{content}</blockquote>\n'
        return html

    def _generate_columns(self, columns_data: Dict[str, Any], images_dir: str = None) -> str:
        """
        生成多栏布局 HTML

        Args:
            columns_data: 多栏布局数据
            images_dir: 图片文件夹路径

        Returns:
            HTML 字符串
        """
        columns = columns_data.get('columns', 2)
        content = columns_data.get('content', '')

        # 确定CSS类名
        class_name = f'{columns}-column' if columns in [2, 3] else 'two-column'

        html = f'<div class="{class_name}">\n'
        html += f'    <p class="no-indent">{content}</p>\n'
        html += '</div>\n'

        return html


if __name__ == '__main__':
    # 测试代码
    import sys
    import json

    if len(sys.argv) < 2:
        print("用法: python word_html_generator.py <解析结果JSON文件>")
        sys.exit(1)

    json_file = sys.argv[1]

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            parsed_content = json.load(f)

        generator = WordHTMLGenerator()
        html = generator.generate(parsed_content, images_dir='images')

        print(html)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
