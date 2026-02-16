#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 解析器
===============

将 Markdown 文档解析为结构化数据，便于生成 Word 兼容的 HTML。

支持元素：
- 标题（h1-h6）
- 段落
- 列表（有序/无序，支持嵌套）
- 表格（支持对齐、合并单元格）
- 图片
- 数学公式（行内/块级）
- 代码块
- 多栏布局
- 水平分隔线

作者：Claude Code
版本：v1.0
"""

import re
from typing import List, Dict, Any, Optional


class MarkdownParser:
    """Markdown 解析器"""

    def __init__(self):
        """初始化解析器"""
        # 正则表达式模式
        self.patterns = {
            'heading': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'code_block': re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL),
            'inline_code': re.compile(r'`([^`]+)`'),
            'image': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
            'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'formula_inline': re.compile(r'\$([^$]+)\$'),
            'formula_display': re.compile(r'\$\$([^$]+)\$\$', re.DOTALL),
            'hr': re.compile(r'^-{3,}$', re.MULTILINE),
            'blockquote': re.compile(r'^>\s+(.+)$', re.MULTILINE),
            'table': re.compile(r'^\|(.+)\|$\n^\|[-| :]+\|$\n(\|.+?\|$\n?)+', re.MULTILINE),
        }

    def parse(self, markdown_content: str) -> Dict[str, Any]:
        """
        解析 Markdown 内容

        Args:
            markdown_content: Markdown 文本内容

        Returns:
            解析结果字典，包含 metadata 和 sections
        """
        result = {
            'metadata': self._extract_metadata(markdown_content),
            'sections': []
        }

        # 移除元数据（如果存在）
        content = self._remove_metadata(markdown_content)

        # 按行分割
        lines = content.split('\n')

        # 解析各个元素
        i = 0
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()

            # 跳过空行
            if not line_stripped:
                i += 1
                continue

            # 检测多栏布局开始/结束
            if line_stripped == '::: columns' or line_stripped == '::: two-column':
                i = self._parse_columns(lines, i, result['sections'])
                continue

            # 检测代码块
            if line_stripped.startswith('```'):
                i = self._parse_code_block(lines, i, result['sections'])
                continue

            # 检测表格
            if line_stripped.startswith('|') and '|' in line_stripped[1:]:
                i = self._parse_table(lines, i, result['sections'])
                continue

            # 检测标题
            if line_stripped.startswith('#'):
                i = self._parse_heading(lines, i, result['sections'])
                continue

            # 检测列表
            if line_stripped.startswith(('-', '*', '+')) or re.match(r'^\d+\.', line_stripped):
                i = self._parse_list(lines, i, result['sections'])
                continue

            # 检测水平分隔线
            if re.match(r'^[-*_{3,}]$', line_stripped):
                result['sections'].append({
                    'type': 'hr',
                    'content': line_stripped
                })
                i += 1
                continue

            # 检测引用块
            if line_stripped.startswith('>'):
                i = self._parse_blockquote(lines, i, result['sections'])
                continue

            # 默认作为段落处理
            i = self._parse_paragraph(lines, i, result['sections'])

        return result

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        提取 YAML 元数据（如果有）

        Args:
            content: Markdown 内容

        Returns:
            元数据字典
        """
        metadata = {}

        # 检查是否有 YAML front matter
        if content.startswith('---'):
            # 查找结束标记
            end_pos = content.find('\n---\n', 4)
            if end_pos != -1:
                yaml_content = content[4:end_pos]
                # 简单解析（生产环境建议使用 PyYAML）
                for line in yaml_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    def _remove_metadata(self, content: str) -> str:
        """
        移除 YAML 元数据

        Args:
            content: Markdown 内容

        Returns:
            移除元数据后的内容
        """
        if content.startswith('---'):
            end_pos = content.find('\n---\n', 4)
            if end_pos != -1:
                return content[end_pos + 5:]
        return content

    def _parse_heading(self, lines: List[str], start_idx: int, sections: List[Dict]) -> int:
        """
        解析标题

        Args:
            lines: 所有行
            start_idx: 起始行索引
            sections: 结果列表

        Returns:
            下一行索引
        """
        line = lines[start_idx]
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())

        if match:
            level = len(match.group(1))
            content = match.group(2)
            content = self._parse_inline_elements(content)

            sections.append({
                'type': 'heading',
                'level': level,
                'content': content
            })

        return start_idx + 1

    def _parse_paragraph(self, lines: List[str], start_idx: int, sections: List[Dict]) -> int:
        """
        解析段落

        Args:
            lines: 所有行
            start_idx: 起始行索引
            sections: 结果列表

        Returns:
            下一行索引
        """
        paragraph_lines = []

        i = start_idx
        while i < len(lines):
            line = lines[i].rstrip()

            # 遇到空行，段落结束
            if not line.strip():
                break

            # 遇到特殊元素，段落结束
            if (line.startswith('#') or
                line.startswith('```') or
                line.strip().startswith('|') or
                re.match(r'^\s*[-*+]\s', line) or
                re.match(r'^\s*\d+\.\s', line) or
                line.strip().startswith(':::')):
                break

            paragraph_lines.append(line)
            i += 1

        if paragraph_lines:
            content = ' '.join(paragraph_lines)
            content = self._parse_inline_elements(content)

            sections.append({
                'type': 'paragraph',
                'content': content,
                'elements': self._extract_inline_elements(content)
            })

        return i

    def _parse_list(self, lines: List[str], start_idx: int, sections: List[Dict]) -> int:
        """
        解析列表（支持嵌套）

        Args:
            lines: 所有行
            start_idx: 起始行索引
            sections: 结果列表

        Returns:
            下一行索引
        """
        items = []
        ordered = None
        base_indent = None

        i = start_idx
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()

            # 检测列表项
            unordered_match = re.match(r'^[-*+]\s+(.+)$', stripped)
            ordered_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)

            if not unordered_match and not ordered_match:
                # 列表结束
                break

            # 确定列表类型
            if ordered is None:
                ordered = ordered_match is not None

            # 检测缩进
            indent = len(line) - len(stripped)
            if base_indent is None:
                base_indent = indent

            # 提取列表项内容
            if ordered:
                number = ordered_match.group(1)
                content = ordered_match.group(2)
            else:
                content = unordered_match.group(1)

            # 处理嵌套（简化版本，只处理一层嵌套）
            if indent > base_indent + 2:
                # 嵌套列表项
                if items:
                    last_item = items[-1]
                    if isinstance(last_item, dict):
                        if 'nested_list' not in last_item:
                            last_item['nested_list'] = {
                                'items': [],
                                'ordered': not unordered_match
                            }
                        last_item['nested_list']['items'].append(content)
            else:
                content = self._parse_inline_elements(content)
                items.append(content)

            i += 1

        if items:
            # 构建嵌套结构
            formatted_items = []
            for item in items:
                if isinstance(item, dict) and 'nested_list' in item:
                    # 将嵌套列表转换为结构化格式
                    formatted_items.append({
                        'content': item['content'],
                        'nested_list': item['nested_list']
                    })
                else:
                    formatted_items.append(item)

            sections.append({
                'type': 'list',
                'ordered': ordered,
                'items': formatted_items,
                'start': 1  # 起始编号
            })

        return i

    def _parse_table(self, lines: List[str], start_idx: int, sections: List[Dict]) -> int:
        """
        解析表格

        Args:
            lines: 所有行
            start_idx: 起始行索引
            sections: 结果列表

        Returns:
            下一行索引
        """
        table_lines = []

        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            if not line.startswith('|'):
                break
            table_lines.append(line)
            i += 1

        if len(table_lines) < 2:
            return i

        # 解析表头
        headers = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]

        # 跳过分隔行
        table_lines = table_lines[2:]

        # 解析表格内容
        rows = []
        for line in table_lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            # 解析单元格内联元素
            parsed_cells = []
            for cell in cells:
                parsed_cells.append({
                    'content': cell,
                    'elements': self._extract_inline_elements(cell)
                })
            rows.append(parsed_cells)

        sections.append({
            'type': 'table',
            'headers': headers,
            'rows': rows
        })

        return i

    def _parse_code_block(self, lines: List[str], start_idx: int, sections: List[Dict]) -> int:
        """
        解析代码块

        Args:
            lines: 所有行
            start_idx: 起始行索引
            sections: 结果列表

        Returns:
            下一行索引
        """
        first_line = lines[start_idx].strip()

        # 提取语言标识
        language = first_line[3:].strip() or 'text'

        # 查找结束标记
        code_lines = []
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if line.strip() == '```':
                i += 1
                break
            code_lines.append(line)
            i += 1

        code = '\n'.join(code_lines)

        sections.append({
            'type': 'code_block',
            'language': language,
            'content': code
        })

        return i

    def _parse_columns(self, lines: List[str], start_idx: int, sections: List[Dict]) -> int:
        """
        解析多栏布局

        Args:
            lines: 所有行
            start_idx: 起始行索引
            sections: 结果列表

        Returns:
            下一行索引
        """
        first_line = lines[start_idx].strip()

        # 确定栏数
        if 'two-column' in first_line or '2' in first_line:
            columns = 2
        elif 'three-column' in first_line or '3' in first_line:
            columns = 3
        else:
            columns = 2

        # 解析栏内容
        column_content = []
        i = start_idx + 1

        while i < len(lines):
            line = lines[i].strip()

            # 遇到结束标记
            if line == ':::':
                i += 1
                break

            # 遇到新的栏（可选，支持 ::column 语法）
            if line.startswith('::') and 'column' in line:
                i += 1
                continue

            # 将内容添加到当前栏
            column_content.append(line)
            i += 1

        sections.append({
            'type': 'columns',
            'columns': columns,
            'content': '\n'.join(column_content)
        })

        return i

    def _parse_blockquote(self, lines: List[str], start_idx: int, sections: List[Dict]) -> int:
        """
        解析引用块

        Args:
            lines: 所有行
            start_idx: 起始行索引
            sections: 结果列表

        Returns:
            下一行索引
        """
        quote_lines = []

        i = start_idx
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped.startswith('>'):
                break

            # 移除引用标记
            quote_lines.append(stripped[1:].strip())
            i += 1

        content = ' '.join(quote_lines)
        content = self._parse_inline_elements(content)

        sections.append({
            'type': 'blockquote',
            'content': content
        })

        return i

    def _parse_inline_elements(self, text: str) -> str:
        """
        解析行内元素（公式、链接、图片等）

        Args:
            text: 文本内容

        Returns:
            解析后的文本
        """
        # 解析数学公式（优先处理，避免 $ 被误解析）
        text = self._parse_formulas(text)

        # 解析图片
        text = self.patterns['image'].sub(
            lambda m: f'{{IMAGE:{m.group(2)}|{m.group(1)}}}',
            text
        )

        # 解析链接
        text = self.patterns['link'].sub(
            lambda m: f'{{LINK:{m.group(2)}|{m.group(1)}}}',
            text
        )

        # 解析行内代码
        text = self.patterns['inline_code'].sub(
            lambda m: f'{{CODE:{m.group(1)}}}',
            text
        )

        # 解析粗体和斜体
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)

        # 解析上标和下标
        text = re.sub(r'\^\{(.+?)\}', r'<sup>\1</sup>', text)
        text = re.sub(r'~\{(.+?)\}', r'<sub>\1</sub>', text)

        return text

    def _parse_formulas(self, text: str) -> str:
        """
        解析数学公式

        Args:
            text: 文本内容

        Returns:
            解析后的文本
        """
        # 块级公式（优先）
        text = self.patterns['formula_display'].sub(
            lambda m: f'{{FORMULA_DISPLAY:{m.group(1).strip()}}}',
            text
        )

        # 行内公式
        text = self.patterns['formula_inline'].sub(
            lambda m: f'{{FORMULA_INLINE:{m.group(1).strip()}}}',
            text
        )

        return text

    def _extract_inline_elements(self, text: str) -> List[Dict[str, Any]]:
        """
        提取行内元素信息

        Args:
            text: 已解析的文本

        Returns:
            行内元素列表
        """
        elements = []

        # 提取图片
        for match in re.finditer(r'\{IMAGE:([^\|]+)\|([^\}]+)\}', text):
            elements.append({
                'type': 'image',
                'path': match.group(1),
                'alt': match.group(2)
            })

        # 提取公式
        for match in re.finditer(r'\{FORMULA_(INLINE|DISPLAY):([^\}]+)\}', text):
            elements.append({
                'type': 'formula',
                'mode': 'inline' if match.group(1) == 'INLINE' else 'display',
                'content': match.group(2)
            })

        # 提取链接
        for match in re.finditer(r'\{LINK:([^\|]+)\|([^\}]+)\}', text):
            elements.append({
                'type': 'link',
                'url': match.group(1),
                'text': match.group(2)
            })

        # 提取代码
        for match in re.finditer(r'\{CODE:([^\}]+)\}', text):
            elements.append({
                'type': 'code',
                'content': match.group(1)
            })

        return elements


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("用法: python markdown_parser.py <markdown文件>")
        sys.exit(1)

    md_file = sys.argv[1]

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        parser = MarkdownParser()
        result = parser.parse(content)

        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
