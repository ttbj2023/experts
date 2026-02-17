#!/usr/bin/env python3
"""
将包含LaTeX公式的Markdown转换为Word文档
公式转换为OMML格式，可在Word公式编辑器中编辑
"""

import re
import sys
from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from latex2mathml.converter import convert as latex_to_mathml
from mathml2omml import convert as mathml_to_omml


def convert_latex_to_omml(latex_formula):
    """将LaTeX公式转换为OMML格式"""
    try:
        mathml = latex_to_mathml(latex_formula)
        omml = mathml_to_omml(mathml)
        return omml
    except Exception as e:
        print(f"⚠️  公式转换失败: {e}")
        return None


def extract_and_convert_formulas(content):
    """
    从Markdown内容提取并转换所有LaTeX公式

    Args:
        content: Markdown文本

    Returns:
        tuple: (converted_content, formulas_list)
        - converted_content: 替换LaTeX为占位符的内容
        - formulas_list: [(position, omml_formula), ...]
    """
    formulas = []
    converted_content = content

    # 块级公式：\[ ... \] 或 $$ ... $$
    display_pattern = r'\\\[([^]]+?)\\\]|\$\$([^$]+)\$\$'

    def replace_display_formula(match):
        latex = match.group(1) or match.group(2)
        omml = convert_latex_to_omml(latex)
        if omml:
            placeholder = f"[[FORMULA_{len(formulas)}]]"
            formulas.append((match.start(), omml))
            return placeholder
        return match.group(0)  # 保留原文本

    converted_content = re.sub(display_pattern, replace_display_formula, content, flags=re.DOTALL)

    # 行内公式：\( ... \) 或 $...$
    inline_pattern = r'\\\(([^)]+?)\\\)|\$([^$]+)\$'

    def replace_inline_formula(match):
        latex = match.group(1) or match.group(2)
        omml = convert_latex_to_omml(latex)
        if omml:
            placeholder = f"[[FORMULA_{len(formulas)}]]"
            formulas.append((match.start(), omml))
            return placeholder
        return match.group(0)

    converted_content = re.sub(inline_pattern, replace_inline_formula, converted_content)

    return converted_content, formulas


def convert_markdown_to_word(md_path, docx_path):
    """
    将Markdown文件转换为Word文档，LaTeX公式转为OMML

    Args:
        md_path: Markdown文件路径
        docx_path: 输出Word文档路径
    """
    print(f"📖 读取Markdown文件: {md_path}")

    # 读取Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取并转换公式
    print("🔄 正在转换LaTeX公式...")
    converted_content, formulas = extract_and_convert_formulas(content)

    print(f"✅ 成功转换 {len(formulas)} 个公式")

    # 创建Word文档
    doc = Document()

    # 处理内容（简化版，按行分割）
    lines = converted_content.split('\n')
    current_formula_index = 0

    for line in lines:
        line = line.strip()
        if not line:
            doc.add_paragraph()
            continue

        # 检查是否为公式占位符
        formula_match = re.match(r'\[\[FORMULA_(\d+)\]\]', line)
        if formula_match:
            formula_idx = int(formula_match.group(1))
            if formula_idx < len(formulas):
                # 插入OMML公式到Word
                omml = formulas[formula_idx][1]
                para = doc.add_paragraph()
                try:
                    # 将OMML字符串直接插入Word段落
                    # 使用from_string方法解析OMML
                    from docx.oxml.ns import qn
                    oxml = OxmlElement(f'<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">{omml}</m:oMathPara>')
                    para._element.append(oxml)
                except Exception as e:
                    print(f"⚠️  插入公式失败: {e}")
                    # 失败时显示占位符
                    para.add_run(f"[公式 {formula_idx + 1}]")
                current_formula_index += 1
                continue

        # 处理标题
        if line.startswith('# '):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            doc.add_heading(text, level=min(level, 9))
        # 处理列表
        elif line.startswith('- ') or line.startswith('* '):
            text = line.lstrip('*-').strip()
            doc.add_paragraph(text, style='List Bullet')
        elif re.match(r'^\d+\. ', line):
            text = re.sub(r'^\d+\. ', '', line).strip()
            doc.add_paragraph(text, style='List Number')
        # 普通段落
        else:
            # 简化Markdown格式（粗体等）
            line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            doc.add_paragraph(line)

    # 保存文档
    doc.save(docx_path)
    print(f"✅ Word文档已保存: {docx_path}")
    return docx_path


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 convert_md_to_word_with_formulas.py <input.md> <output.docx>")
        sys.exit(1)

    md_path = sys.argv[1]
    docx_path = sys.argv[2]

    # 检查输入文件
    if not Path(md_path).exists():
        print(f"❌ 错误: Markdown文件不存在: {md_path}")
        sys.exit(1)

    # 转换
    try:
        convert_markdown_to_word(md_path, docx_path)
        print("\n🎉 转换完成！")
        print(f"请在Word中打开 {docx_path} 查看效果")
        print("公式应该可以双击编辑")
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
