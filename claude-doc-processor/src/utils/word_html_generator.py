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

    def generate(self, parsed_content: Dict[str, Any], images_dir: str = None, md_file_dir: str = None) -> str:
        """
        生成完整的 HTML 文档

        Args:
            parsed_content: 解析后的 Markdown 内容
            images_dir: 图片文件夹路径（用于相对路径转 base64）
            md_file_dir: Markdown 文件所在目录（用于查找相对路径图片）

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
            html_parts.append(self._generate_section(section, images_dir, md_file_dir))

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
        生成 Word 兼容的 CSS 样式（完全从模板配置读取）

        Returns:
            style 标签内的 CSS 内容
        """
        # ========== 从配置读取样式参数 ==========
        # 字体和颜色
        font_family = self.config.get('default_font', '宋体')
        western_font = self.config.get('western_font', 'Times New Roman')
        heading_font = self.config.get('heading_font', '黑体')
        text_color = self.config.get('text_color', '#000000')
        heading_color = self.config.get('heading_color', '#000000')
        link_color = self.config.get('link_color', '#0000FF')

        # 字号
        body_font_size = self.config.get('default_font_size', 12)
        h1_size = self.config.get('heading1_size', 18)
        h2_size = self.config.get('heading2_size', 16)
        h3_size = self.config.get('heading3_size', 14)
        h4_size = self.config.get('heading4_size', 12)
        h5_size = self.config.get('heading5_size', 12)
        h6_size = self.config.get('heading6_size', 12)

        # 行距
        line_height = self.config.get('line_height', 1.5)

        # 页面边距
        page_margin_top = self.config.get('page_margin_top', '20pt')
        page_margin_bottom = self.config.get('page_margin_bottom', '20pt')
        page_margin_left = self.config.get('page_margin_left', '30pt')
        page_margin_right = self.config.get('page_margin_right', '30pt')
        body_padding_top = self.config.get('page_padding_top', page_margin_top)
        body_padding_bottom = self.config.get('page_padding_bottom', page_margin_bottom)
        body_padding_left = self.config.get('page_padding_left', page_margin_left)
        body_padding_right = self.config.get('page_padding_right', page_margin_right)

        # 段落样式
        para_first_line_indent = self.config.get('paragraph_first_line_indent', '2em')
        para_text_align = self.config.get('paragraph_text_align', 'justify')
        para_spacing_before = self.config.get('paragraph_spacing_before', 0)
        para_spacing_after = self.config.get('paragraph_spacing_after', 12)

        # 标题样式
        h1_align = self.config.get('heading1_align', 'center')
        h1_margin_top = self.config.get('heading1_margin_top', 24)
        h1_margin_bottom = self.config.get('heading1_margin_bottom', 18)
        h1_page_break_before = self.config.get('heading1_page_break_before', False)

        h2_align = self.config.get('heading2_align', 'left')
        h2_margin_top = self.config.get('heading2_margin_top', 18)
        h2_margin_bottom = self.config.get('heading2_margin_bottom', 12)
        h2_page_break_before = self.config.get('heading2_page_break_before', False)

        h3_align = self.config.get('heading3_align', 'left')
        h3_margin_top = self.config.get('heading3_margin_top', 14)
        h3_margin_bottom = self.config.get('heading3_margin_bottom', 6)

        h4_align = self.config.get('heading4_align', 'left')
        h4_margin_top = self.config.get('heading4_margin_top', 12)
        h4_margin_bottom = self.config.get('heading4_margin_bottom', 6)

        # 表格样式
        table_border_color = self.config.get('table_border_color', '#000000')
        table_border_width = self.config.get('table_border_width', '1px')
        table_cell_padding = self.config.get('table_cell_padding', '4pt')
        table_header_bg = self.config.get('table_header_bg', '#f0f0f0')

        # 代码块样式
        code_font = self.config.get('code_font', 'Courier New')
        code_bg = self.config.get('code_background_color', '#f5f5f5')
        code_padding = self.config.get('code_padding', '10pt')

        # 标书特殊配置
        table_content_font_size = self.config.get('table_content_font_size', 10.5)
        caption_font_size = self.config.get('heading1_size', 16)  # 标书标题字号

        # 生成CSS
        styles = f'''    <style type="text/css">
        /* ==================== 全局样式 ==================== */
        body {{
            font-family: '{font_family}', '{western_font}', serif;
            font-size: {body_font_size}pt;
            line-height: {line_height};
            color: {text_color};
            margin: 0;
            padding: {body_padding_top} {body_padding_right} {body_padding_bottom} {body_padding_left};
            text-align: {para_text_align};
        }}

        /* ==================== 标题样式 ==================== */
        h1 {{
            font-family: '{heading_font}', '{font_family}', sans-serif;
            font-size: {h1_size}pt;
            font-weight: bold;
            color: {heading_color};
            text-align: {h1_align};
            margin-top: {h1_margin_top}pt;
            margin-bottom: {h1_margin_bottom}pt;
            page-break-after: avoid;
            {'page-break-before: always;' if h1_page_break_before else ''}
        }}

        h2 {{
            font-family: '{heading_font}', '{font_family}', sans-serif;
            font-size: {h2_size}pt;
            font-weight: bold;
            color: {heading_color};
            text-align: {h2_align};
            margin-top: {h2_margin_top}pt;
            margin-bottom: {h2_margin_bottom}pt;
            page-break-after: avoid;
            {'page-break-before: always;' if h2_page_break_before else ''}
        }}

        h3 {{
            font-family: '{heading_font}', '{font_family}', sans-serif;
            font-size: {h3_size}pt;
            font-weight: bold;
            color: {heading_color};
            text-align: {h3_align};
            margin-top: {h3_margin_top}pt;
            margin-bottom: {h3_margin_bottom}pt;
            page-break-after: avoid;
        }}

        h4 {{
            font-family: '{heading_font}', '{font_family}', sans-serif;
            font-size: {h4_size}pt;
            font-weight: bold;
            color: {heading_color};
            text-align: {h4_align};
            margin-top: {h4_margin_top}pt;
            margin-bottom: {h4_margin_bottom}pt;
            page-break-after: avoid;
        }}

        h5 {{
            font-family: '{heading_font}', '{font_family}', sans-serif;
            font-size: {h5_size}pt;
            font-weight: bold;
            color: {heading_color};
            margin-top: 12pt;
            margin-bottom: 6pt;
        }}

        h6 {{
            font-family: '{heading_font}', '{font_family}', sans-serif;
            font-size: {h6_size}pt;
            font-weight: normal;
            color: {heading_color};
            margin-top: 12pt;
            margin-bottom: 6pt;
        }}

        /* ==================== 段落样式 ==================== */
        p {{
            margin-top: {para_spacing_before}pt;
            margin-bottom: {para_spacing_after}pt;
            text-indent: {para_first_line_indent};
            text-align: {para_text_align};
        }}

        p.no-indent {{
            text-indent: 0;
        }}

        p.center {{
            text-align: center;
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
            font-family: '{code_font}', monospace;
            background-color: {code_bg};
            padding: 2pt 4pt;
        }}

        a {{
            color: {link_color};
            text-decoration: underline;
        }}

        /* ==================== 列表样式 ==================== */
        ul, ol {{
            margin: {para_spacing_before}pt {para_spacing_after}pt;
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

        td {{
            border: {table_border_width} solid {table_border_color};
            padding: {table_cell_padding};
            text-align: center;
            font-size: {table_content_font_size}pt;  /* 表格内容字号 */
        }}

        th {{
            border: {table_border_width} solid {table_border_color};
            padding: {table_cell_padding};
            text-align: center;
            font-weight: bold;
            background-color: {table_header_bg};
            font-size: {caption_font_size}pt;  /* 表标题字号 */
        }}

        /* 表图标题样式 */
        .table-caption {{
            text-align: center;
            font-size: {caption_font_size}pt;
            font-weight: bold;
            margin: 8pt 0;
        }}

        .figure-caption {{
            text-align: center;
            font-size: {caption_font_size}pt;
            font-weight: bold;
            margin: 5pt 0;
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

        /* ==================== 公式样式 ==================== */
        .formula-block {{
            margin: 8pt 0;
            text-align: center;
            break-inside: avoid;
        }}

        /* ==================== 代码块样式 ==================== */
        pre {{
            background-color: {code_bg};
            padding: {code_padding};
            margin: 10pt 0;
            font-family: '{code_font}', monospace;
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

        /* ==================== 技术文档特殊样式 ==================== */
        /* 特殊提示框样式 */
        .callout {{
            margin: 10pt 0;
            padding: 8pt 12pt;
            border-left: 4pt solid;
            break-inside: avoid;
        }}

        .callout-note {{
            border-color: #0366D6;
            background-color: #F6F8FA;
        }}

        .callout-warning {{
            border-color: #B08800;
            background-color: #FFFBDD;
        }}

        .callout-error {{
            border-color: #CB2431;
            background-color: #ffeef0;
        }}

        .callout-tip {{
            border-color: #28A745;
            background-color: #F0FFF4;
        }}

        .callout-title {{
            font-weight: bold;
            margin-bottom: 4pt;
        }}

        /* API端点样式 */
        .api-endpoint {{
            margin: 10pt 0;
            padding: 8pt;
            background-color: #F6F8FA;
            border: 1px solid #E1E4E8;
            border-radius: 6px;
            font-family: '{code_font}', monospace;
        }}

        .api-method {{
            display: inline-block;
            padding: 2pt 6pt;
            border-radius: 4px;
            font-weight: bold;
            font-size: 9pt;
            color: #FFFFFF;
            margin-right: 8pt;
        }}

        .api-method-GET {{ background-color: #28A745; }}
        .api-method-POST {{ background-color: #0366D6; }}
        .api-method-PUT {{ background-color: #F6A945; }}
        .api-method-DELETE {{ background-color: #CB2431; }}
        .api-method-PATCH {{ background-color: #6F42C1; }}

        .api-path {{
            font-weight: bold;
            color: #24292E;
        }}

        /* 键盘快捷键样式 */
        kbd {{
            display: inline-block;
            padding: 2pt 6pt;
            font-family: '{code_font}', monospace;
            font-size: 9pt;
            background-color: #FAFAFA;
            border: 1px solid #CCCCCC;
            border-radius: 3pt;
            box-shadow: 0 1pt 1px rgba(0,0,0,0.2);
        }}

        /* 标签样式 */
        .tag {{
            display: inline-block;
            padding: 2pt 6pt;
            font-size: 8pt;
            border-radius: 10pt;
            background-color: #F6F8FA;
            color: #586069;
            border: 1px solid #E1E4E8;
            margin: 0 2pt;
        }}

        /* 版本标签样式 */
        .version-badge {{
            display: inline-block;
            padding: 2pt 6pt;
            font-size: 8pt;
            border-radius: 3pt;
            background-color: #0366D6;
            color: #FFFFFF;
            font-weight: bold;
        }}

        /* 代码语言标签 */
        .code-language {{
            display: inline-block;
            padding: 2pt 6pt;
            font-size: 8pt;
            border-radius: 3pt 3pt 0 0;
            background-color: #E1E4E8;
            color: #586069;
            font-family: '{code_font}', monospace;
            margin-bottom: -4pt;
        }}

        /* 链接样式增强 */
        a.external {{
            padding-right: 12pt;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 16 16"><path fill="%230366D6" d="M10.5 8.5L14 12l-3.5 3.5M14 8H6v8h8"/></svg>');
            background-repeat: no-repeat;
            background-position: right center;
        }}

        /* 参数表格样式 */
        table.parameter-table td:nth-child(1) {{
            width: 20%;
            font-weight: bold;
            font-family: '{code_font}', monospace;
        }}

        table.parameter-table td:nth-child(2) {{
            width: 15%;
            font-family: '{code_font}', monospace;
            color: #0366D6;
        }}

        table.parameter-table td:nth-child(3) {{
            width: 65%;
        }}

        /* 状态指示器 */
        .status {{
            display: inline-block;
            width: 8pt;
            height: 8pt;
            border-radius: 50%;
            margin-right: 4pt;
        }}

        .status-success {{ background-color: #28A745; }}
        .status-warning {{ background-color: #F6A945; }}
        .status-error {{ background-color: #CB2431; }}
        .status-info {{ background-color: #0366D6; }}

        /* 水平分隔线 ==================== */
        hr {{
            border: none;
            border-top: 1pt solid #ccc;
            margin: 15pt 0;
        }}

        /* ==================== 页面控制 ==================== */
        @page {{
            size: A4;
            margin: {page_margin_top} {page_margin_right} {page_margin_bottom} {page_margin_left};
        }}

        /* 防止元素被拆分 */
        .no-break {{
            break-inside: avoid;
        }}
    </style>'''

        return styles
    def _generate_section(self, section: Dict[str, Any], images_dir: str = None, md_file_dir: str = None) -> str:
        """
        生成单个章节/元素的 HTML

        Args:
            section: 章节数据
            images_dir: 图片文件夹路径
            md_file_dir: Markdown 文件所在目录

        Returns:
            HTML 字符串
        """
        element_type = section.get('type')

        if element_type == 'heading':
            return self._generate_heading(section)

        elif element_type == 'paragraph':
            return self._generate_paragraph(section, images_dir, md_file_dir)

        elif element_type == 'list':
            return self._generate_list(section)

        elif element_type == 'table':
            return self._generate_table(section, md_file_dir)

        elif element_type == 'code_block':
            return self._generate_code_block(section)

        elif element_type == 'hr':
            return '<hr>\n'

        elif element_type == 'blockquote':
            return self._generate_blockquote(section)

        elif element_type == 'columns':
            return self._generate_columns(section, images_dir, md_file_dir)

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

        # 替换公式占位符
        content_with_formulas = self._replace_formulas_in_text(content)

        # 防止标题被拆分
        html = f'<div style="break-inside: avoid;">\n'
        html += f'    <h{level}>{content_with_formulas}</h{level}>\n'
        html += '</div>\n'

        return html

    def _generate_paragraph(self, paragraph: Dict[str, Any], images_dir: str = None, md_file_dir: str = None) -> str:
        """
        生成段落 HTML

        Args:
            paragraph: 段落数据
            images_dir: 图片文件夹路径
            md_file_dir: Markdown 文件所在目录

        Returns:
            HTML 字符串
        """
        content = paragraph.get('content', '')
        elements = paragraph.get('elements', [])

        # 处理图片元素
        if any(e.get('type') == 'image' for e in elements):
            return self._generate_paragraph_with_image(paragraph, images_dir, md_file_dir)

        # 处理公式元素
        if any(e.get('type') == 'formula' for e in elements):
            return self._generate_paragraph_with_formula(paragraph)

        # 普通段落也要替换公式占位符
        content_with_formulas = self._replace_formulas_in_text(content)

        # 解析 Markdown 内联元素（粗体、斜体、删除线）
        content_with_markdown = self._parse_inline_markdown(content_with_formulas)

        # 处理行内代码
        content_final = self._parse_inline_code(content_with_markdown)

        # 处理代码占位符 {CODE:text}
        content_final = re.sub(r'\{CODE:([^}]+)\}', r'<code>\1</code>', content_final)

        html = f'<p>{content_final}</p>\n'
        return html

    def _generate_paragraph_with_image(self, paragraph: Dict[str, Any], images_dir: str = None, md_file_dir: str = None) -> str:
        """
        生成包含图片的段落

        Args:
            paragraph: 段落数据
            images_dir: 图片文件夹路径
            md_file_dir: Markdown 文件所在目录

        Returns:
            HTML 字符串
        """
        content = paragraph.get('content', '')
        elements = paragraph.get('elements', [])
        html = ''

        # 首先替换公式占位符为 MathJax 标签
        content_with_formulas = self._replace_formulas_in_text(content)

        # 解析 Markdown 内联元素（粗体、斜体、删除线）
        content_with_markdown = self._parse_inline_markdown(content_with_formulas)

        # 处理行内代码
        content_with_code = self._parse_inline_code(content_with_markdown)

        # 处理代码占位符 {CODE:text}
        import re
        content_with_code = re.sub(r'\{CODE:([^}]+)\}', r'<code>\1</code>', content_with_code)

        # 移除图片占位符（{IMAGE:path|alt}）避免在文本中显示
        content_cleaned = re.sub(r'\{IMAGE:[^\|]+\|[^\}]+\}', '', content_with_code).strip()

        # 首先输出段落文本内容
        if content_cleaned:
            html += f'<p>{content_cleaned}</p>\n'

        # 然后输出图片（不带标题）
        for element in elements:
            if element.get('type') == 'image':
                image_path = element.get('path', '')
                alt_text = element.get('alt', '图片')

                # 尝试多个路径查找图片
                possible_paths = []

                # 1. 原始路径（可能是绝对或相对）
                possible_paths.append(image_path)

                # 2. 如果是相对路径，尝试相对于当前工作目录
                if not os.path.isabs(image_path):
                    possible_paths.append(os.path.abspath(image_path))

                # 3. 如果提供了 images_dir，尝试相对于 images_dir
                if images_dir:
                    possible_paths.append(os.path.join(images_dir, os.path.basename(image_path)))
                    possible_paths.append(os.path.join(images_dir, image_path))

                # 4. 如果提供了 md_file_dir，尝试相对于 Markdown 文件所在目录
                if md_file_dir and not os.path.isabs(image_path):
                    possible_paths.append(os.path.join(md_file_dir, image_path))
                    possible_paths.append(os.path.join(md_file_dir, os.path.basename(image_path)))

                # 找到第一个存在的路径
                actual_path = None
                for path in possible_paths:
                    if os.path.isfile(path):
                        actual_path = path
                        break

                if actual_path:
                    try:
                        data_uri = self.image_encoder.encode_image(actual_path)
                        html += f'<p><img src="{data_uri}" alt="{alt_text}"></p>\n'
                    except Exception as e:
                        html += f'<p>[图片编码失败: {alt_text}: {str(e)}]</p>\n'
                else:
                    html += f'<p>[图片未找到: {alt_text} (路径: {image_path})]</p>\n'

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

        # 使用统一的公式替换方法（会转换为 MathML）
        content = self._replace_formulas_in_text(content)

        # 解析 Markdown 内联元素（粗体、斜体、删除线）
        content = self._parse_inline_markdown(content)

        # 处理行内代码
        content = self._parse_inline_code(content)

        # 处理代码占位符 {CODE:text}
        content = re.sub(r'\{CODE:([^}]+)\}', r'<code>\1</code>', content)

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
                content = self._replace_formulas_in_text(item['content'])
                html += f'    <li>{content}\n'
                html += self._generate_nested_list(item['nested_list'])
                html += '    </li>\n'
            else:
                # 处理普通列表项
                content = self._replace_formulas_in_text(item)
                html += f'    <li>{content}</li>\n'

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
            content = self._replace_formulas_in_text(item)
            html += f'    <li>{content}</li>\n'

        html += f'</{tag}>\n'
        return html

    def _generate_table(self, table_data: Dict[str, Any], md_file_dir: str = None) -> str:
        """
        生成表格 HTML

        Args:
            table_data: 表格数据
            md_file_dir: Markdown 文件所在目录（用于查找图片）

        Returns:
            HTML 字符串
        """
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        aligns = table_data.get('aligns', [])  # 获取对齐信息

        html = '<table border="1" cellpadding="4" cellspacing="0" width="100%">\n'

        # 表头
        if headers:
            html += '    <thead>\n'
            html += '        <tr>\n'
            for i, header in enumerate(headers):
                # 获取对齐方式，默认居中
                align = aligns[i] if i < len(aligns) else 'center'
                # 替换公式
                content = self._replace_formulas_in_text(header)
                # 解析 Markdown 内联元素（粗体、斜体、删除线）
                content = self._parse_inline_markdown(content)
                html += f'            <th align="{align}">{content}</th>\n'
            html += '        </tr>\n'
            html += '    </thead>\n'

        # 表体
        html += '    <tbody>\n'
        for row in rows:
            html += '        <tr>\n'
            for i, cell in enumerate(row):
                # 获取对齐方式，默认居中
                align = aligns[i] if i < len(aligns) else 'center'

                content = cell.get('content', '')
                elements = cell.get('elements', [])

                # 替换公式占位符
                content = self._replace_formulas_in_text(content)

                # 解析 Markdown 内联元素（粗体、斜体、删除线）
                content = self._parse_inline_markdown(content)

                # 替换 Markdown 图片语法为嵌入的 base64 图片
                content = self._replace_markdown_images(content, md_file_dir)

                # 移除图片占位符（{IMAGE:path|alt}）避免在文本中显示
                import re
                content_cleaned = re.sub(r'\{IMAGE:[^\|]+\|[^\}]+\}', '', content).strip()

                # 如果单元格包含图片元素，需要嵌入图片
                if any(e.get('type') == 'image' for e in elements):
                    # 先输出文本内容
                    if content_cleaned:
                        html += f'            <td align="{align}">{content_cleaned}<br>'
                    else:
                        html += f'            <td align="{align}"'

                    # 然后输出图片
                    for element in elements:
                        if element.get('type') == 'image':
                            image_path = element.get('path', '')
                            alt_text = element.get('alt', '图片')

                            # 尝试多个路径查找图片
                            possible_paths = []
                            possible_paths.append(image_path)

                            if not os.path.isabs(image_path):
                                possible_paths.append(os.path.abspath(image_path))

                            # 尝试相对于 Markdown 文件的路径
                            if md_file_dir and not os.path.isabs(image_path):
                                possible_paths.append(os.path.join(md_file_dir, image_path))
                                possible_paths.append(os.path.join(md_file_dir, os.path.basename(image_path)))

                            # 找到第一个存在的路径
                            actual_path = None
                            for path in possible_paths:
                                if os.path.isfile(path):
                                    actual_path = path
                                    break

                            if actual_path:
                                try:
                                    data_uri = self.image_encoder.encode_image(actual_path)
                                    html += f'<img src="{data_uri}" alt="{alt_text}"><br>'
                                except Exception as e:
                                    html += f'[图片编码失败: {alt_text}]<br>'
                            else:
                                html += f'[图片未找到: {alt_text} (路径: {image_path})]<br>'

                    html += '</td>\n'
                else:
                    html += f'            <td align="{align}">{content_cleaned}</td>\n'
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

        # 替换公式占位符
        content = self._replace_formulas_in_text(content)

        # 解析 Markdown 内联元素（粗体、斜体、删除线）
        content = self._parse_inline_markdown(content)

        # 处理行内代码（简单转义显示）
        content = self._parse_inline_code(content)

        html = f'<blockquote>{content}</blockquote>\n'
        return html

    def _generate_columns(self, columns_data: Dict[str, Any], images_dir: str = None, md_file_dir: str = None) -> str:
        """
        生成多栏布局 HTML

        Args:
            columns_data: 多栏布局数据
            images_dir: 图片文件夹路径
            md_file_dir: Markdown 文件所在目录

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

    def _replace_markdown_images(self, text: str, md_file_dir: str = None) -> str:
        """
        替换 Markdown 图片语法为嵌入的 base64 图片

        Args:
            text: 包含 markdown 图片语法的文本
            md_file_dir: Markdown 文件所在目录（用于查找图片）

        Returns:
            替换后的文本
        """
        import re

        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)

            # 尝试多个路径查找图片
            possible_paths = []
            possible_paths.append(image_path)

            if not os.path.isabs(image_path):
                possible_paths.append(os.path.abspath(image_path))

            # 尝试相对于 Markdown 文件的路径
            if md_file_dir and not os.path.isabs(image_path):
                possible_paths.append(os.path.join(md_file_dir, image_path))
                possible_paths.append(os.path.join(md_file_dir, os.path.basename(image_path)))

            # 找到第一个存在的路径
            actual_path = None
            for path in possible_paths:
                if os.path.isfile(path):
                    actual_path = path
                    break

            if actual_path:
                try:
                    data_uri = self.image_encoder.encode_image(actual_path)
                    return f'<img src="{data_uri}" alt="{alt_text}">'
                except Exception as e:
                    return f'[图片编码失败: {alt_text}]'
            else:
                return f'[图片未找到: {alt_text}]'

        # 替换所有 ![alt](path) 格式的图片
        return re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', replace_image, text)

    def _replace_formulas_in_text(self, text: str) -> str:
        """
        在文本中替换公式占位符为 MathML（Word 公式编辑器可识别）

        同时支持：
        - 占位符格式: {FORMULA_INLINE:...} 和 {FORMULA_DISPLAY:...}
        - Markdown 格式: $...$ 和 $$...$$

        Args:
            text: 包含公式占位符的文本

        Returns:
            替换后的文本
        """
        # 导入 LaTeX 到 MathML 转换器
        try:
            from latex2mathml.converter import convert as latex_to_mathml
        except ImportError:
            # 如果没有 latex2mathml，回退到 MathJax
            self.logger.warning("latex2mathml 未安装，公式将使用 MathJax 格式（Word 不可编辑）")
            return self._replace_formulas_with_mathjax(text)

        result = text

        # 第一步：处理 Markdown 公式语法 $...$ 和 $$...$$
        import re

        def replace_inline_formula(match):
            """替换内联公式 $...$"""
            latex_content = match.group(1)
            try:
                mathml = latex_to_mathml(latex_content)
                return mathml
            except Exception as e:
                self.logger.warning(f"LaTeX 转换 MathML 失败: {latex_content}, 错误: {e}")
                return f'<span style="color: red;">${latex_content}$</span>'

        def replace_display_formula(match):
            """替换块级公式 $$...$$"""
            latex_content = match.group(1)
            try:
                mathml = latex_to_mathml(latex_content)
                # 块级公式：设置 display="block"
                mathml = mathml.replace('display="inline"', 'display="block"')
                return mathml
            except Exception as e:
                self.logger.warning(f"LaTeX 转换 MathML 失败: {latex_content}, 错误: {e}")
                return f'<span style="color: red;">$${latex_content}$$</span>'

        def replace_inline_latex(match):
            r"""替换 LaTeX 内联公式 \(...\)"""
            latex_content = match.group(1)
            try:
                mathml = latex_to_mathml(latex_content)
                return mathml
            except Exception as e:
                self.logger.warning(f"LaTeX 转换 MathML 失败: {latex_content}, 错误: {e}")
                return f'<span style="color: red;">\\({latex_content}\\)</span>'

        def replace_display_latex(match):
            r"""替换 LaTeX 块级公式 \[...\]"""
            latex_content = match.group(1)
            try:
                mathml = latex_to_mathml(latex_content)
                # 块级公式：设置 display="block"
                mathml = mathml.replace('display="inline"', 'display="block"')
                return mathml
            except Exception as e:
                self.logger.warning(f"LaTeX 转换 MathML 失败: {latex_content}, 错误: {e}")
                return f'<span style="color: red;">\\[{latex_content}\\]</span>'

        # 先处理块级公式 $$...$$（避免与内联公式冲突）
        result = re.sub(r'\$\$([^\$]+)\$\$', replace_display_formula, result)

        # 再处理内联公式 $...$
        result = re.sub(r'\$([^\$]+)\$', replace_inline_formula, result)

        # 然后处理 LaTeX 块级公式 \[...\]
        result = re.sub(r'\\\[([^\]]+)\\\]', replace_display_latex, result)

        # 最后处理 LaTeX 内联公式 \(...\)
        result = re.sub(r'\\\(([^\)]+)\\\)', replace_inline_latex, result)

        # 第五步：处理 LaTeX 环境 \begin{equation}...\end{equation}
        def replace_latex_environment(match):
            """替换 LaTeX 环境 \begin{env}...\end{env}"""
            full_match = match.group(0)
            env_name = match.group(1)
            content = match.group(2)

            # 提取环境内容（去除多余的空白）
            content = content.strip()

            # 只处理 equation 类环境（数学公式）
            math_envs = ['equation', 'align', 'gather', 'multline']
            if env_name.lower() in math_envs:
                try:
                    mathml = latex_to_mathml(content)
                    # 块级公式：设置 display="block"
                    mathml = mathml.replace('display="inline"', 'display="block"')
                    return mathml
                except Exception as e:
                    self.logger.warning(f"LaTeX 环境 {env_name} 转换 MathML 失败: {content}, 错误: {e}")
                    return f'<span style="color: red;">\\begin{{{env_name}}} {content} \\end{{{env_name}}}</span>'
            else:
                # 非数学环境，保持原样
                return full_match

        # 匹配 \begin{env}...\end{env}
        # 使用非贪婪模式匹配环境内容
        result = re.sub(
            r'\\begin\{([^}]+)\}(.*?)\\end\{\1\}',
            replace_latex_environment,
            result,
            flags=re.DOTALL
        )

        # 第二步：处理占位符格式 {FORMULA_INLINE:...} 和 {FORMULA_DISPLAY:...}
        offset = 0
        text = result  # 使用已经处理过 Markdown 公式的文本

        while True:
            # 查找公式占位符开始
            start = text.find('{FORMULA_', offset)
            if start == -1:
                break

            # 提取类型和内容
            type_end = text.find(':', start)
            if type_end == -1:
                break

            formula_type = text[start+9:type_end]  # 跳过 '{FORMULA_'

            # 手动查找配对的结束花括号
            brace_count = 0
            i = type_end + 1
            content_start = i

            while i < len(text):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    if brace_count == 0:
                        # 找到配对的结束括号
                        formula_content = text[content_start:i]

                        # 使用 latex2mathml 转换为 MathML
                        try:
                            mathml = latex_to_mathml(formula_content)

                            # 根据公式类型设置 display 属性
                            if formula_type == 'DISPLAY':
                                # 块级公式：添加 display="block"
                                mathml = mathml.replace('display="inline"', 'display="block"')

                            formula_html = mathml
                        except Exception as e:
                            # 转换失败，使用原始 LaTeX 文本作为回退
                            self.logger.warning(f"LaTeX 转换 MathML 失败: {formula_content}, 错误: {e}")
                            formula_html = f'<span style="color: red;">LaTeX: {formula_content}</span>'

                        # 替换
                        result = result[:start] + formula_html + result[i+1:]
                        # 重新开始搜索（因为字符串已经改变）
                        text = result
                        offset = start + len(formula_html)
                        break
                    else:
                        brace_count -= 1
                i += 1
            else:
                # 未找到配对的结束括号
                offset = start + 1

        return result

    def _parse_inline_markdown(self, text: str) -> str:
        """
        解析 Markdown 内联元素：粗体、斜体、删除线

        注意：不支持行内代码（Word 中不需要）

        Args:
            text: 包含 Markdown 语法的文本

        Returns:
            替换后的 HTML 文本
        """
        import re
        result = text

        # 注意：处理顺序很重要
        # 1. 先处理删除线（~~text~~）
        result = re.sub(r'~~([^~]+)~~', r'<s>\1</s>', result)

        # 2. 处理粗斜体（***text***）
        result = re.sub(r'\*\*\*([^*]+)\*\*\*', r'<strong><em>\1</em></strong>', result)

        # 3. 处理粗体（**text** 或 __text__）
        result = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', result)
        result = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', result)

        # 4. 处理斜体（*text* 或 _text_）
        result = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', result)
        result = re.sub(r'_([^_]+)_', r'<em>\1</em>', result)

        return result

    def _parse_inline_code(self, text: str) -> str:
        """
        解析行内代码（简单处理）

        Args:
            text: 包含行内代码的文本

        Returns:
            替换后的 HTML 文本
        """
        import re
        # 将行内代码转换为 <code> 标签，保留原始内容
        result = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return result

    def _replace_formulas_with_mathjax(self, text: str) -> str:
        """
        使用 MathJax 格式替换公式（回退方案，Word 不可编辑）

        Args:
            text: 包含公式占位符的文本

        Returns:
            替换后的文本
        """
        # 手动解析公式占位符（支持嵌套花括号）
        result = text
        offset = 0

        while True:
            # 查找公式占位符开始
            start = text.find('{FORMULA_', offset)
            if start == -1:
                break

            # 提取类型和内容
            type_end = text.find(':', start)
            if type_end == -1:
                break

            formula_type = text[start+9:type_end]  # 跳过 '{FORMULA_'

            # 手动查找配对的结束花括号
            brace_count = 0
            i = type_end + 1
            content_start = i

            while i < len(text):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    if brace_count == 0:
                        # 找到配对的结束括号
                        formula_content = text[content_start:i]

                        # 生成 MathJax 标签
                        if formula_type == 'DISPLAY':
                            formula_html = f'<script type="math/tex; mode=display">{formula_content}</script>'
                        else:  # INLINE
                            formula_html = f'<script type="math/tex">{formula_content}</script>'

                        # 替换
                        result = result[:start] + formula_html + result[i+1:]
                        # 重新开始搜索（因为字符串已经改变）
                        text = result
                        offset = start + len(formula_html)
                        break
                    else:
                        brace_count -= 1
                i += 1
            else:
                # 未找到配对的结束括号
                offset = start + 1

        return result


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
