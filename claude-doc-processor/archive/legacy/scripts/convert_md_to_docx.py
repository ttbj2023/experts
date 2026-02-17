#!/usr/bin/env python3
"""
Markdown转DOCX转换器（专业版）
使用python-docx和pypands结合，提供更好的表格和格式支持
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
except ImportError:
    print("错误：缺少python-docx库")
    print("安装命令：pip3 install python-docx")
    sys.exit(1)


class MarkdownToDocxConverter:
    """Markdown转DOCX转换器"""

    def __init__(self):
        self.doc = Document()
        self._setup_styles()

    def _setup_styles(self):
        """设置文档样式"""
        # 设置中文字体
        self.doc.styles['Normal'].font.name = '宋体'
        self.doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        self.doc.styles['Normal'].font.size = Pt(11)

    def parse_markdown(self, content: str):
        """解析Markdown内容"""
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()

            # 空行
            if not line.strip():
                i += 1
                continue

            # 标题（# ## ### 等）
            if line.startswith('#'):
                level = len(re.match(r'^#+', line).group())
                text = line.lstrip('#').strip()
                self._add_heading(text, level)
                i += 1
                continue

            # 表格
            if line.startswith('|') and i + 1 < len(lines):
                table = self._parse_table(lines, i)
                if table:
                    i += table[1]  # 跳过表格的所有行
                    continue

            # 引用块（> 开头）
            if line.startswith('>'):
                self._add_blockquote(lines, i)
                i += 1
                continue

            # 代码块
            if line.startswith('```'):
                i = self._parse_code_block(lines, i)
                continue

            # 普通段落
            self._add_paragraph(line)
            i += 1

    def _add_heading(self, text: str, level: int):
        """添加标题"""
        heading = self.doc.add_heading(text, level=min(level, 9))
        # 设置中文字体
        for run in heading.runs:
            run.font.name = '黑体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    def _add_paragraph(self, text: str):
        """添加普通段落"""
        para = self.doc.add_paragraph()

        # 处理行内代码 `...`
        parts = re.split(r'`([^`]+)`', text)
        for i, part in enumerate(parts):
            if i % 2 == 1:  # 代码部分
                run = para.add_run(part)
                run.font.name = 'Consolas'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(199, 37, 78)  # 红色
            else:  # 普通文本
                # 处理粗体 **...**
                bold_parts = re.split(r'\*\*([^*]+)\*\*', part)
                for j, bold_part in enumerate(bold_parts):
                    if j % 2 == 1:  # 粗体部分
                        run = para.add_run(bold_part)
                        run.bold = True
                        run.font.name = '宋体'
                    else:
                        # 处理数学公式 $...$
                        math_parts = re.split(r'\$([^$]+)\$', bold_part)
                        for k, math_part in enumerate(math_parts):
                            if k % 2 == 1:  # 数学公式
                                run = para.add_run(math_part)
                                run.font.name = 'Cambria Math'
                                run.font.italic = True
                            else:
                                if math_part:
                                    para.add_run(math_part)

    def _parse_table(self, lines: List[str], start_idx: int) -> Tuple[bool, int]:
        """解析表格"""
        if not lines[start_idx].startswith('|'):
            return False, 0

        # 收集表格所有行
        table_lines = []
        i = start_idx
        while i < len(lines) and lines[i].startswith('|'):
            table_lines.append(lines[i])
            i += 1
            # 遇到分隔线后继续（Markdown表格有分隔线）
            if i < len(lines) and lines[i].startswith('|---'):
                table_lines.append(lines[i])
                i += 1

        if len(table_lines) < 2:
            return False, 0

        # 解析表格内容
        rows_data = []
        for line in table_lines:
            # 跳过分隔线
            if '|---' in line:
                continue
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            rows_data.append(cells)

        if not rows_data:
            return False, 0

        # 创建表格
        table = self.doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
        table.style = 'Light Grid Accent 1'

        # 填充数据
        for row_idx, row_data in enumerate(rows_data):
            row = table.rows[row_idx]
            for cell_idx, cell_text in enumerate(row_data):
                cell = row.cells[cell_idx]
                cell.text = cell_text

                # 表头加粗
                if row_idx == 0:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True

        return True, i - start_idx

    def _add_blockquote(self, lines: List[str], start_idx: int):
        """添加引用块"""
        para = self.doc.add_paragraph()
        para_style = para.paragraph_format
        para_style.left_indent = Inches(0.5)
        para_style.right_indent = Inches(0.5)

        text = lines[start_idx].lstrip('>').strip()
        run = para.add_run(text)
        run.font.color.rgb = RGBColor(128, 128, 128)  # 灰色
        run.font.italic = True

    def _parse_code_block(self, lines: List[str], start_idx: int) -> int:
        """解析代码块"""
        if not lines[start_idx].startswith('```'):
            return start_idx + 1

        # 找到代码块结束
        end_idx = start_idx + 1
        while end_idx < len(lines) and not lines[end_idx].startswith('```'):
            end_idx += 1

        if end_idx >= len(lines):
            return start_idx + 1

        # 提取代码
        code_lines = lines[start_idx + 1:end_idx]
        code_text = '\n'.join(code_lines)

        # 添加代码块
        para = self.doc.add_paragraph()
        run = para.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(199, 37, 78)

        return end_idx + 1

    def save(self, output_path: str):
        """保存文档"""
        self.doc.save(output_path)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 convert_md_to_docx.py <markdown文件> [输出文件]")
        print("\n示例:")
        print("  python3 convert_md_to_docx.py input.md")
        print("  python3 convert_md_to_docx.py input.md output.docx")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"错误：文件不存在 - {input_file}")
        sys.exit(1)

    # 确定输出文件
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.parent / f"{input_file.stem}.docx"

    # 读取Markdown
    print(f"📖 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 转换
    print("🔄 转换为DOCX...")
    converter = MarkdownToDocxConverter()
    converter.parse_markdown(content)

    # 保存
    print(f"💾 保存到: {output_file}")
    converter.save(str(output_file))

    # 统计信息
    print("\n📊 转换统计:")
    print(f"   输入文件: {input_file}")
    print(f"   输出文件: {output_file}")
    print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")

    print("\n✅ 转换完成！")


if __name__ == '__main__':
    main()
