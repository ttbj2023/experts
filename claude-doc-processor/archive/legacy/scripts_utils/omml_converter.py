#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMML to LaTeX Converter

从DOCX中提取OMML格式的数学公式并转换为LaTeX格式
支持公式验证和错误处理
"""

import re
import xml.etree.ElementTree as ET
from typing import Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OMMLConverter:
    """OMML公式转LaTeX转换器"""

    def __init__(self):
        """初始化转换器"""
        self.conversion_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'fallback_to_image': 0
        }

    def omml_to_latex(self, omml_xml: str) -> Tuple[bool, str]:
        """
        将OMML格式转换为LaTeX格式

        Args:
            omml_xml: OMML格式的XML字符串

        Returns:
            (success, latex_code): 转换是否成功和LaTeX代码
        """
        self.conversion_stats['total'] += 1

        try:
            # 清理XML字符串
            omml_xml = omml_xml.strip()

            # 解析OMML XML
            root = ET.fromstring(omml_xml)

            # 提取公式并转换为LaTeX
            latex_code = self._parse_omml_element(root)

            if latex_code:
                self.conversion_stats['success'] += 1
                logger.debug(f"OMML转LaTeX成功: {latex_code}")
                return True, latex_code
            else:
                self.conversion_stats['failed'] += 1
                logger.warning("OMML转LaTeX失败: 无法解析公式内容")
                return False, None

        except Exception as e:
            self.conversion_stats['failed'] += 1
            logger.error(f"OMML转LaTeX异常: {str(e)}")
            return False, None

    def _parse_omml_element(self, element: ET.Element) -> Optional[str]:
        """
        递归解析OMML元素

        Args:
            element: XML元素

        Returns:
            LaTeX字符串或None
        """
        # OMML命名空间
        ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}

        # 处理分数 m:f
        if element.tag.endswith('}f'):
            return self._parse_fraction(element, ns)

        # 处理上标 m:sSup
        elif element.tag.endswith('}sSup'):
            return self._parse_superscript(element, ns)

        # 处理下标 m:sSub
        elif element.tag.endswith('}sSub'):
            return self._parse_subscript(element, ns)

        # 处理上下标 m:sSubSup
        elif element.tag.endswith('}sSubSup'):
            return self._parse_subscript_superscript(element, ns)

        # 处理根号 m:rad
        elif element.tag.endswith('}rad'):
            return self._parse_radical(element, ns)

        # 处理n次根号 m:radDeg
        elif element.tag.endswith('}radPr') or element.tag.endswith('}deg'):
            return self._parse_radical(element, ns)

        # 处理求和 m:nary
        elif element.tag.endswith('}nary'):
            return self._parse_nary(element, ns)

        # 处理积分 m:nary (积分符为∫)
        elif element.tag.endswith('}func'):
            return self._parse_function(element, ns)

        # 处理矩阵 m:m
        elif element.tag.endswith('}m'):
            return self._parse_matrix(element, ns)

        # 处理括号 m:d
        elif element.tag.endswith('}d'):
            return self._parse_delimiter(element, ns)

        # 处理文本运行 m:r
        elif element.tag.endswith('}r'):
            return self._parse_run(element, ns)

        # 处理文本 m:t
        elif element.tag.endswith('}t'):
            return element.text or ''

        # 处理分隔符
        elif element.tag.endswith('}punct'):
            return ','

        # 默认：尝试处理子元素
        return self._parse_children(element, ns)

    def _parse_fraction(self, element: ET.Element, ns: dict) -> str:
        """解析分数 m:f"""
        numerator = ""
        denominator = ""

        for child in element:
            if child.tag.endswith('}num'):
                numerator = self._parse_omml_element(child) or ""
            elif child.tag.endswith('}den'):
                denominator = self._parse_omml_element(child) or ""

        if numerator and denominator:
            return f"\\frac{{{numerator}}}{{{denominator}}}"
        return ""

    def _parse_superscript(self, element: ET.Element, ns: dict) -> str:
        """解析上标 m:sSup"""
        base = ""
        sup = ""

        for child in element:
            if child.tag.endswith('}e'):
                # 第一个e是底数，第二个e是上标
                if not base:
                    base = self._parse_omml_element(child) or ""
                else:
                    sup = self._parse_omml_element(child) or ""

        if base and sup:
            return f"{{{base}}}^{{{sup}}}"
        return base or ""

    def _parse_subscript(self, element: ET.Element, ns: dict) -> str:
        """解析下标 m:sSub"""
        base = ""
        sub = ""

        for child in element:
            if child.tag.endswith('}e'):
                if not base:
                    base = self._parse_omml_element(child) or ""
                else:
                    sub = self._parse_omml_element(child) or ""

        if base and sub:
            return f"{{{base}_{{{sub}}}}}"
        return base or ""

    def _parse_subscript_superscript(self, element: ET.Element, ns: dict) -> str:
        """解析上下标 m:sSubSup"""
        base = ""
        sub = ""
        sup = ""

        for child in element:
            if child.tag.endswith('}e'):
                if not base:
                    base = self._parse_omml_element(child) or ""
                elif not sub:
                    sub = self._parse_omml_element(child) or ""
                else:
                    sup = self._parse_omml_element(child) or ""

        if base:
            if sub and sup:
                return f"{{{base}_{{{sub}}}^{{{sup}}}}}"
            elif sub:
                return f"{{{base}_{{{sub}}}}}"
            elif sup:
                return f"{{{base}}}^{{{sup}}}"
        return base or ""

    def _parse_radical(self, element: ET.Element, ns: dict) -> str:
        """解析根号 m:rad"""
        base = ""
        deg = ""  # 次数

        for child in element:
            if child.tag.endswith('}deg'):
                deg = self._parse_omml_element(child) or ""
            elif child.tag.endswith('}e'):
                base = self._parse_omml_element(child) or ""

        if base:
            if deg and deg != '2':
                return f"\\sqrt[{deg}]{{{base}}}"
            else:
                return f"\\sqrt{{{base}}}"
        return ""

    def _parse_nary(self, element: ET.Element, ns: dict) -> str:
        """解析求和/积分等n元运算符 m:nary"""
        # 查找运算符符号
        nary_pr = element.find('.//m:naryPr', ns)
        if nary_pr is not None:
            char_elem = nary_pr.find('.//m:chr', ns)
            if char_elem is not None and char_elem.get('m:val'):
                char = char_elem.get('m:val')
            else:
                char = '∑'  # 默认求和符号
        else:
            char = '∑'

        # 提取下限、上限和底数
        sub = ""
        sup = ""
        base = ""

        for child in element:
            if child.tag.endswith('}sub'):
                sub = self._parse_omml_element(child) or ""
            elif child.tag.endswith('}sup'):
                sup = self._parse_omml_element(child) or ""
            elif child.tag.endswith('}e'):
                base = self._parse_omml_element(child) or ""

        # 根据符号选择LaTeX命令
        if char == '∑':
            cmd = 'sum'
        elif char == '∫':
            cmd = 'int'
        elif char == '∏':
            cmd = 'prod'
        else:
            cmd = 'operatorname{{{}}}'.format(char)

        if sub or sup:
            limits = f"_{{{sub}}}" if sub else ""
            limits += f"^{{{sup}}}" if sup else ""
            return f"\\{cmd}{limits} {{{base}}}"
        else:
            return f"\\{cmd} {{{base}}}"

    def _parse_function(self, element: ET.Element, ns: dict) -> str:
        """解析函数 m:func"""
        func_name = ""
        args = []

        for child in element:
            if child.tag.endswith('}fName'):
                func_name = self._parse_omml_element(child) or ""
            elif child.tag.endswith('}e'):
                arg = self._parse_omml_element(child)
                if arg:
                    args.append(arg)

        if func_name and args:
            return f"\\{func_name}({', '.join(args)})"
        return ""

    def _parse_matrix(self, element: ET.Element, ns: dict) -> str:
        """解析矩阵 m:m"""
        rows = []

        for child in element:
            if child.tag.endswith('}mr'):
                # 矩阵行
                elements = []
                for e in child.findall('.//m:e', ns):
                    elem_content = self._parse_omml_element(e)
                    if elem_content:
                        elements.append(elem_content)

                if elements:
                    rows.append(' & '.join(elements))

        if rows:
            matrix_content = ' \\\\\n'.join(rows)
            return f"\\begin{{pmatrix}}\n{matrix_content}\n\\end{{pmatrix}}"
        return ""

    def _parse_delimiter(self, element: ET.Element, ns: dict) -> str:
        """解析括号 m:d"""
        content = ""

        for child in element:
            if child.tag.endswith('}e'):
                content = self._parse_omml_element(child) or ""

        # 查找括号字符
        d_pr = element.find('.//m:dPr', ns)
        if d_pr is not None:
            beg_char = d_pr.find('.//m:begChr', ns)
            end_char = d_pr.find('.//m:endChr', ns)

            beg = beg_char.get('m:val') if beg_char is not None else '('
            end = end_char.get('m:val') if end_char is not None else ')'

            return f"{beg}{content}{end}"

        return f"({content})"

    def _parse_run(self, element: ET.Element, ns: dict) -> str:
        """解析文本运行 m:r"""
        texts = []

        for child in element:
            if child.tag.endswith('}t'):
                text = child.text
                if text:
                    texts.append(text)

        return ''.join(texts)

    def _parse_children(self, element: ET.Element, ns: dict) -> str:
        """解析子元素"""
        parts = []

        for child in element:
            result = self._parse_omml_element(child)
            if result:
                parts.append(result)

        return ''.join(parts)

    def get_stats(self) -> dict:
        """获取转换统计信息"""
        return self.conversion_stats.copy()

    def reset_stats(self):
        """重置统计信息"""
        self.conversion_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'fallback_to_image': 0
        }


def test_conversion():
    """测试转换功能"""
    converter = OMMLConverter()

    # 测试分数: 1/2
    test_omml = """
    <m:f xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
        <m:num><m:r><m:t>1</m:t></m:r></m:num>
        <m:den><m:r><m:t>2</m:t></m:r></m:den>
    </m:f>
    """

    success, latex = converter.omml_to_latex(test_omml)
    print(f"测试结果: {success}, LaTeX: {latex}")
    print(f"统计信息: {converter.get_stats()}")


if __name__ == "__main__":
    test_conversion()
