#!/usr/bin/env python3
"""
LaTeX公式转Word可编辑格式转换器

使用latex2mathml将LaTeX公式转换为OMML格式（Word原生支持）
"""

import re
import sys
from latex2mathml.converter import convert as latex_to_mathml
from mathml2omml import convert as mathml_to_omml


def convert_latex_to_omml(latex_formula):
    """
    将LaTeX公式转换为OMML格式（Word公式编辑器支持）

    Args:
        latex_formula: LaTeX公式字符串

    Returns:
        OMML格式的公式字符串（可插入Word）

    Example:
        >>> latex = r"\frac{a}{b}"
        >>> omml = convert_latex_to_omml(latex)
    """
    try:
        # LaTeX → MathML
        mathml = latex_to_mathml(latex_formula)

        # MathML → OMML (Word格式)
        omml = mathml_to_omml(mathml)

        return omml

    except Exception as e:
        print(f"⚠️  公式转换失败: {e}")
        print(f"   LaTeX公式: {latex_formula[:50]}...")
        return None


def extract_latex_formulas(content):
    """
    从Markdown内容中提取所有LaTeX公式

    Args:
        content: Markdown文本

    Returns:
        list of tuples: [(formula_type, latex_formula, position)]
        - formula_type: 'inline' 或 'display'
        - latex_formula: LaTeX公式字符串
        - position: 在原文中的位置
    """
    formulas = []

    # 块级公式：\[ ... \] 或 $$ ... $$
    display_pattern = r'\\\[\s*(.*?)\s*\\\]|\$\$([^$]+)\$\$'
    for match in re.finditer(display_pattern, content, re.DOTALL):
        latex = match.group(1) or match.group(2)
        formulas.append(('display', latex, match.start()))

    # 行内公式：\( ... \) 或 $...$
    inline_pattern = r'\\\(\s*(.*?)\s*\\\)|\$([^$]+)\$'
    for match in re.finditer(inline_pattern, content):
        # 跳过已在块级公式中匹配的
        is_nested = any(f[2] < match.start() < match.start() < f[2] + len(f[1])
                        for f in formulas)
        if not is_nested:
            latex = match.group(1) or match.group(2)
            formulas.append(('inline', latex, match.start()))

    # 按位置排序
    formulas.sort(key=lambda x: x[2])

    return formulas


def test_conversion():
    """测试LaTeX到OMML转换功能"""
    test_cases = [
        (r"\frac{a}{b}", "简单分数"),
        (r"\overline{x} = \frac{x_1 + x_2}{n}", "平均数公式"),
        (r"\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}", "微积分公式"),
    ]

    print("🧪 测试LaTeX到OMML转换...\n")

    for latex, description in test_cases:
        print(f"测试: {description}")
        print(f"LaTeX: {latex}")

        omml = convert_latex_to_omml(latex)
        if omml:
            print(f"✅ 转换成功！")
            print(f"OMML长度: {len(omml)} 字符")
            print(f"OMML预览: {omml[:100]}...")
        else:
            print("❌ 转换失败")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_conversion()
    else:
        print("LaTeX公式转Word OMML格式转换器")
        print("\n使用方法:")
        print("  python3 latex_to_word_formula.py --test     # 运行测试")
        print("\n功能:")
        print("  - 将LaTeX公式转换为Word OMML格式")
        print("  - 支持行内公式: \\(...\\) 或 $...$")
        print("  - 支持块级公式: \\[...\\] 或 $$...$$")
