#!/usr/bin/env python3
"""
Markdown转DOCX转换器（增强版）
专门优化表格处理和格式保留
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("错误：缺少python-docx库")
    print("安装命令：pip3 install python-docx")
    sys.exit(1)


def set_cell_background(cell, color: str):
    """设置单元格背景色"""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color)
    cell._element.get_or_add_tcPr().append(shading_elm)


def set_cell_border(cell, **kwargs):
    """设置单元格边框"""
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')

    for edge in ['top', 'left', 'bottom', 'right']:
        if edge in kwargs:
            edge_elm = OxmlElement(f'w:{edge}')
            for key, value in kwargs[edge].items():
                edge_elm.set(qn(f'w:{key}'), str(value))
            tcBorders.append(edge_elm)

    tcPr.append(tcBorders)


class EnhancedMarkdownToDocxConverter:
    """增强版Markdown转DOCX转换器"""

    def __init__(self):
        self.doc = Document()
        self._setup_styles()
        self.table_counter = 0

    def _setup_styles(self):
        """设置文档样式"""
        # 设置默认字体
        style = self.doc.styles['Normal']
        style.font.name = '宋体'
        style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        style.font.size = Pt(11)

        # 设置页面边距
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1.25)
            section.right_margin = Inches(1.25)

    def parse_markdown(self, content: str):
        """解析Markdown内容"""
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()

            # 跳过空行
            if not line.strip():
                i += 1
                continue

            # 标题
            if line.startswith('#'):
                level = len(re.match(r'^#+', line).group())
                text = line.lstrip('#').strip()
                self._add_heading(text, level)
                i += 1
                continue

            # 表格
            if line.startswith('|'):
                table_rows = self._parse_table_lines(lines, i)
                if table_rows and len(table_rows) >= 2:
                    self._add_table(table_rows)
                    i += len(table_rows)
                    continue

            # 引用块
            if line.startswith('>'):
                self._add_blockquote(line)
                i += 1
                continue

            # 代码块
            if line.startswith('```'):
                i = self._parse_code_block(lines, i)
                continue

            # 分隔线
            if re.match(r'^[-*]{3,}$', line.strip()):
                self.doc.add_paragraph('_' * 50)
                i += 1
                continue

            # 普通段落
            self._add_paragraph(line)
            i += 1

    def _add_heading(self, text: str, level: int):
        """添加标题"""
        heading = self.doc.add_heading(text, level=min(level, 9))

        # 设置中文字体和样式
        for run in heading.runs:
            run.font.name = '黑体'
            run.font.size = Pt(16 - level)  # 一级16pt，二级15pt，以此类推
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            run.font.bold = True

    def _add_paragraph(self, text: str):
        """添加段落（支持行内格式）"""
        para = self.doc.add_paragraph()

        # 处理各种行内格式
        parts = re.split(r'(`[^`]+`|\*\*[^*]+\*\*|\$[^$]+\$)', text)

        for i, part in enumerate(parts):
            if not part:
                continue

            # 行内代码
            if part.startswith('`') and part.endswith('`'):
                code_text = part[1:-1]
                run = para.add_run(code_text)
                run.font.name = 'Consolas'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(199, 37, 78)

            # 粗体
            elif part.startswith('**') and part.endswith('**'):
                bold_text = part[2:-2]
                run = para.add_run(bold_text)
                run.bold = True
                run.font.name = '宋体'

            # 数学公式
            elif part.startswith('$') and part.endswith('$'):
                math_text = part[1:-1]
                run = para.add_run(math_text)
                run.font.name = 'Cambria Math'
                run.font.italic = True
                run.font.size = Pt(11)

            # 普通文本
            else:
                para.add_run(part)

    def _parse_table_lines(self, lines: List[str], start_idx: int) -> Optional[List[List[str]]]:
        """解析表格的所有行"""
        if not lines[start_idx].startswith('|'):
            return None

        table_lines = []
        i = start_idx

        while i < len(lines) and lines[i].startswith('|'):
            line = lines[i].strip()

            # 遇到空行或非表格行，结束
            if not line or not line.startswith('|'):
                break

            # 解析单元格
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_lines.append(cells)
            i += 1

        # 检查是否有分隔线（第二行通常是 |---|---|）
        if len(table_lines) >= 2 and re.match(r'^\|?\s*:?-+:?\|', lines[start_idx + 1]):
            # 移除分隔行
            table_lines.pop(1)

        return table_lines if len(table_lines) >= 2 else None

    def _add_table(self, table_data: List[List[str]]):
        """添加表格（增强版）"""
        self.table_counter += 1

        # 创建表格
        rows = len(table_data)
        cols = len(table_data[0])
        table = self.doc.add_table(rows=rows, cols=cols)

        # 设置表格样式
        table.style = 'Light Grid Accent 1'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # 设置表格边框
        border_props = {
            'sz': '4',
            'val': 'single',
            'color': 'auto'
        }

        # 填充数据
        for row_idx, row_data in enumerate(table_data):
            row = table.rows[row_idx]

            # 设置行高
            row.height = Inches(0.3)

            for col_idx, cell_text in enumerate(row_data):
                cell = row.cells[col_idx]

                # 设置单元格边框
                set_cell_border(cell, **{edge: border_props for edge in ['top', 'left', 'bottom', 'right']})

                # 表头样式
                if row_idx == 0:
                    cell.text = cell_text
                    # 设置表头背景色
                    set_cell_background(cell, '4472C4')

                    # 设置表头字体
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        for run in paragraph.runs:
                            run.font.bold = True
                            run.font.size = Pt(11)
                            run.font.color.rgb = RGBColor(255, 255, 255)
                            run.font.name = '宋体'
                            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

                # 数据行样式
                else:
                    cell.text = cell_text

                    # 交替行背景色
                    if row_idx % 2 == 0:
                        set_cell_background(cell, 'D9E2F3')

                    # 设置单元格字体
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        for run in paragraph.runs:
                            run.font.size = Pt(10)
                            run.font.name = '宋体'
                            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

        # 设置表格自动适配
        table.autofit = False
        for row in table.rows:
            for cell in row.cells:
                cell.width = Inches(1.5)

    def _add_blockquote(self, line: str):
        """添加引用块"""
        para = self.doc.add_paragraph()

        # 设置缩进
        para_format = para.paragraph_format
        para_format.left_indent = Inches(0.5)
        para_format.right_indent = Inches(0.5)

        # 提取文本
        text = line.lstrip('>').strip()

        # 设置灰色斜体
        run = para.add_run(text)
        run.font.color.rgb = RGBColor(128, 128, 128)
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
        print("用法: python3 convert_md_to_docx_enhanced.py <markdown文件> [输出文件]")
        print("\n示例:")
        print("  python3 convert_md_to_docx_enhanced.py input.md")
        print("  python3 convert_md_to_docx_enhanced.py input.md output.docx")
        print("\n特性:")
        print("  ✓ 增强的表格样式（边框、背景色、自动对齐）")
        print("  ✓ 表头加粗和白色文字")
        print("  ✓ 交替行背景色（斑马纹）")
        print("  ✓ 中文字体支持（宋体、黑体）")
        print("  ✓ 数学公式字体（Cambria Math）")
        print("  ✓ 代码块样式（Consolas等宽字体）")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"错误：文件不存在 - {input_file}")
        sys.exit(1)

    # 确定输出文件
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.parent / f"{input_file.stem}_enhanced.docx"

    # 读取Markdown
    print(f"📖 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 统计信息
    line_count = len(content.split('\n'))
    table_count = len(re.findall(r'^\|[^|\n]+\|', content, re.MULTILINE))
    heading_count = len(re.findall(r'^#+\s', content, re.MULTILINE))

    print(f"📊 文档统计:")
    print(f"   总行数: {line_count}")
    print(f"   表格数: {table_count}")
    print(f"   标题数: {heading_count}")

    # 转换
    print("\n🔄 转换为DOCX（增强版）...")
    converter = EnhancedMarkdownToDocxConverter()
    converter.parse_markdown(content)

    # 保存
    print(f"💾 保存到: {output_file}")
    converter.save(str(output_file))

    print(f"\n📊 转换结果:")
    print(f"   输入文件: {input_file}")
    print(f"   输出文件: {output_file}")
    print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")
    print(f"   处理表格: {converter.table_counter} 个")

    print("\n✅ 转换完成！")
    print(f"\n💡 提示：在Microsoft Word或WPS Office中打开查看效果")


if __name__ == '__main__':
    main()
