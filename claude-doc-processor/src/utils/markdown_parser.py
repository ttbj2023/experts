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
        last_i = -1  # 防御性检查：记录上一次的索引，用于检测死循环

        while i < len(lines):
            # 防御性检查：检测索引停滞（死循环保护）
            if i == last_i:
                raise ValueError(
                    f"解析器卡死在第 {i+1} 行: {repr(lines[i])}\n"
                    f"这表明元素检测逻辑存在BUG，导致索引无法推进。\n"
                    f"请检查该行内容是否符合预期的元素格式。"
                )
            last_i = i

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

            # 检测水平分隔线（必须在列表检测之前，避免被误判为列表项）
            if re.match(r'^[-*_]{3,}$', line_stripped):
                result['sections'].append({
                    'type': 'hr',
                    'content': line_stripped
                })
                i += 1
                continue

            # 检测列表（使用完整正则，避免误判HR等非列表元素）
            if (re.match(r'^[-*+]\s+', line_stripped) or
                re.match(r'^\d+\.\s+', line_stripped)):
                i = self._parse_list(lines, i, result['sections'])
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
            # 注意：对于 | 开头的行，只有当它是真正的表格行（至少 2 个 |）时才中断
            # 排除几何证明中的单个 | 符号（如 |AB=CD, 表示"因为"）
            line_stripped = line.strip()
            if (line.startswith('#') or
                line.startswith('```') or
                (line_stripped.startswith('|') and line_stripped.count('|') >= 2) or
                re.match(r'^\s*[-*+]\s', line) or
                re.match(r'^\s*\d+\.\s', line) or
                line_stripped.startswith(':::')):
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
            if ordered and ordered_match:
                number = ordered_match.group(1)
                content = ordered_match.group(2)
            elif not ordered and unordered_match:
                content = unordered_match.group(1)
            else:
                # 理论上不会到这里，但作为保险
                break

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
        # 检查第一行是否满足表格条件（至少 2 个 | 符号）
        # 如果不满足，返回 start_idx + 1，让这一行被当作普通段落处理
        first_line = lines[start_idx].strip()
        if not first_line.startswith('|') or first_line.count('|') < 2:
            return start_idx + 1

        table_lines = []

        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            # 表格行必须至少有 2 个 | 符号（首尾各一个）
            # 排除只有一个 | 的情况（如几何证明中的"因为"符号）
            if not line.startswith('|') or line.count('|') < 2:
                break
            table_lines.append(line)
            i += 1

        if len(table_lines) < 2:
            return i

        # 解析表头
        headers = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]

        # 解析分隔行，提取对齐信息
        aligns = []
        if len(table_lines) >= 2:
            separator_cells = [cell.strip() for cell in table_lines[1].split('|')[1:-1]]
            for cell in separator_cells:
                # 判断对齐方式
                if cell.startswith(':') and cell.endswith(':'):
                    aligns.append('center')  # :---:
                elif cell.startswith(':'):
                    aligns.append('left')     # :---
                elif cell.endswith(':'):
                    aligns.append('right')    # ---:
                else:
                    aligns.append('center')   # 默认居中

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
            'aligns': aligns,  # 添加对齐信息
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

        # 解析粗体和斜体（避免匹配公式占位符内部）
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        # 下划线斜体：只匹配字母数字，避免匹配LaTeX公式中的下标
        text = re.sub(r'_(\w+?)_', r'<em>\1</em>', text)

        # 注释：上标和下标功能与LaTeX公式冲突，已禁用
        # LaTex公式使用 ^ 和 _ 作为语法，不应转换为HTML标签
        # text = re.sub(r'\^\{(.+?)\}', r'<sup>\1</sup>', text)
        # text = re.sub(r'~\{(.+?)\}', r'<sub>\1</sub>', text)

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

        # 提取公式（手动解析以支持嵌套花括号）
        formula_start = 0
        while True:
            # 查找公式占位符开始
            start = text.find('{FORMULA_', formula_start)
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
                        elements.append({
                            'type': 'formula',
                            'mode': 'inline' if formula_type == 'INLINE' else 'display',
                            'content': formula_content
                        })
                        formula_start = i + 1
                        break
                    else:
                        brace_count -= 1
                i += 1
            else:
                # 未找到配对的结束括号
                break

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
