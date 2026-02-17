#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将pdftotext的输出转换为规范化的Markdown格式

功能：
1. 识别章节标题并应用Markdown层级
2. 清理多余空白
3. 处理题目编号
4. 尝试修复双栏排版问题
"""

import re
import sys
from pathlib import Path


class PDFToMarkdownConverter:
    def __init__(self):
        # 章节标题识别模式
        self.patterns = {
            'chapter': re.compile(r'^(第[一二三四五六七八九十\d]+章)\s*(.+)$'),
            'section': re.compile(r'^(\d+)\.\s*(.+)$'),
            'subsection': re.compile(r'^(\d+)\.(\d+)\s*(.+)$'),
            'question': re.compile(r'^(\d+)\.\s*([^（）\s][^）]*[）.]?|$)'),
            'answer_choice': re.compile(r'^([A-D])\.'),
            'page_number': re.compile(r'^\d+$'),
            'garbage': re.compile(r'^[􀥈􀪋\s]+$'),
        }

    def clean_line(self, line):
        """清理单行文本"""
        # 去除首尾空白
        line = line.strip()
        # 去除特殊乱码字符
        line = re.sub(r'[􀥈􀪋]', '', line)
        # 合并多个空格为单个空格
        line = re.sub(r'\s+', ' ', line)
        return line

    def is_title(self, line):
        """判断是否为标题"""
        if self.patterns['chapter'].match(line):
            return 'chapter'
        if self.patterns['subsection'].match(line):
            return 'subsection'
        if '重点' in line and len(line) < 50:
            return 'highlight'
        return None

    def convert_title(self, line, title_type):
        """转换标题为Markdown格式"""
        if title_type == 'chapter':
            m = self.patterns['chapter'].match(line)
            if m:
                return f"# {m.group(1)} {m.group(2).strip()}"
        elif title_type == 'subsection':
            m = self.patterns['subsection'].match(line)
            if m:
                title = m.group(3).strip()
                if '[重点]' in title:
                    title = title.replace('[重点]', '**[重点]**')
                return f"## {m.group(1)}.{m.group(2)} {title}"
        elif title_type == 'highlight':
            title = line.replace('[重点]', '**[重点]**')
            return f"### {title}"
        return line

    def should_skip(self, line):
        """判断是否应该跳过该行"""
        if not line:
            return True
        if self.patterns['garbage'].match(line):
            return True
        if self.patterns['page_number'].match(line):
            return True
        if line.strip() == '':
            return True
        return False

    def is_answer_line(self, line):
        """判断是否为答案行"""
        if re.match(r'^[A-D]\.', line):
            return True
        if line.startswith('答案') or line.startswith('解析'):
            return True
        return False

    def process_file(self, input_path, output_path):
        """处理单个文件"""
        print(f"处理: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        result = []
        prev_empty = False
        in_code_block = False

        for raw_line in lines:
            line = self.clean_line(raw_line)

            # 跳过空行和垃圾内容
            if self.should_skip(line):
                if not prev_empty and result:
                    result.append('')  # 保留一个空行
                    prev_empty = True
                continue

            prev_empty = False

            # 检测标题
            title_type = self.is_title(line)
            if title_type:
                md_line = self.convert_title(line, title_type)
                result.append('')
                result.append(md_line)
                result.append('')
                continue

            # 处理题目编号
            if re.match(r'^\d+\.', line):
                # 尝试分割题目和答案（可能是双栏混在一起）
                parts = re.split(r'\s{10,}', line)  # 用大量空格分割
                if len(parts) > 1:
                    # 可能是双栏，取第一部分作为主内容
                    line = parts[0]

                # 高亮题目编号
                line = re.sub(r'^(\d+)\.', r'**\1.**', line)

            # 处理答案选项
            if self.patterns['answer_choice'].match(line):
                line = f"  - {line}"

            # 添加到结果
            result.append(line)

        # 去除连续的空行
        final_result = []
        prev_empty = False
        for line in result:
            if line == '':
                if not prev_empty:
                    final_result.append(line)
                    prev_empty = True
            else:
                final_result.append(line)
                prev_empty = False

        # 写入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_result))

        print(f"✓ 完成: {output_path}")
        print(f"  原始行数: {len(lines)}")
        print(f"  输出行数: {len(final_result)}")

        return len(final_result)


def main():
    if len(sys.argv) < 3:
        print("用法: python convert_pdftotext_to_md.py <input.txt> <output.md>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    converter = PDFToMarkdownConverter()
    converter.process_file(input_file, output_file)


if __name__ == '__main__':
    main()
