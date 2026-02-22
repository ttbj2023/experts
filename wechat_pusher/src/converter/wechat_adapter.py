"""
微信规范适配器
基于《微信公众号排版HTML/CSS开发参考指南》实现
确保HTML完全符合微信公众号的规范要求
"""
import re
from typing import List, Set
from bs4 import BeautifulSoup, Tag, NavigableString

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WeChatAdapter:
    """微信规范适配器"""

    # HTML标签白名单（完全支持）
    ALLOWED_TAGS = {
        "p",
        "span",
        "br",
        "strong",
        "b",
        "em",
        "i",
        "u",
        "del",
        "s",
        "h1",
        "h2",
        "h3",
        "ul",
        "ol",
        "li",
        "blockquote",
        "code",
        "pre",
        "section",
        "div",
        "hr",
        "table",
        "thead",
        "tbody",
        "tr",
        "td",
        "th",
        "img",
        "a",
    }

    # CSS属性白名单
    ALLOWED_CSS_PROPERTIES = {
        # 文本样式
        "font-size",
        "font-weight",
        "font-style",
        "color",
        "text-align",
        "line-height",
        "letter-spacing",
        "text-decoration",
        "text-indent",
        "word-break",
        "white-space",
        # 盒模型与布局
        "width",
        "max-width",
        "min-width",
        "margin",
        "margin-top",
        "margin-right",
        "margin-bottom",
        "margin-left",
        "padding",
        "padding-top",
        "padding-right",
        "padding-bottom",
        "padding-left",
        "display",
        "flex-direction",
        "justify-content",
        "align-items",
        "flex-wrap",
        "flex",
        "gap",
        "box-sizing",
        # 边框与背景
        "border",
        "border-top",
        "border-right",
        "border-bottom",
        "border-left",
        "border-radius",
        "background-color",
        "box-shadow",
        "opacity",
    }

    # 禁用的CSS属性（会被过滤）
    FORBIDDEN_CSS_PROPERTIES = {
        "position",
        "z-index",
        "float",
        "transform",
        "transition",
        "animation",
        "overflow",
        "grid",
        "grid-template-columns",
        "grid-template-rows",
    }

    def __init__(self):
        """初始化适配器"""
        self.stats = {"removed_tags": 0, "removed_styles": 0, "fixed_code_blocks": 0}

    def adapt(self, html: str) -> str:
        """
        适配HTML以符合微信规范

        Args:
            html: 原始HTML

        Returns:
            str: 适配后的HTML
        """
        logger.info("开始微信规范适配")

        # 重置统计信息
        self.stats = {"removed_tags": 0, "removed_styles": 0, "fixed_code_blocks": 0}

        try:
            soup = BeautifulSoup(html, "lxml")

            # 1. 过滤标签
            self._filter_tags(soup)

            # 2. 处理样式（内联化并过滤）
            self._process_styles(soup)

            # 3. 处理代码块
            self._fix_code_blocks(soup)

            # 4. 处理图片
            self._process_images(soup)

            # 5. 处理链接
            self._process_links(soup)

            # 6. 移除不支持的属性
            self._remove_forbidden_attributes(soup)

            # 获取处理后的HTML
            result = str(soup)

            logger.info(
                f"微信规范适配完成: "
                f"移除{self.stats['removed_tags']}个标签, "
                f"移除{self.stats['removed_styles']}个样式, "
                f"修复{self.stats['fixed_code_blocks']}个代码块"
            )

            return result

        except Exception as e:
            logger.error(f"微信规范适配失败: {e}")
            raise

    def _filter_tags(self, soup: BeautifulSoup):
        """
        过滤HTML标签，只保留白名单内的标签

        Args:
            soup: BeautifulSoup对象
        """
        for tag in soup.find_all(True):
            if tag.name not in self.ALLOWED_TAGS:
                # 如果是禁用标签，移除标签但保留内容
                if tag.name in ["script", "style", "iframe", "form", "input"]:
                    tag.decompose()
                    self.stats["removed_tags"] += 1
                else:
                    # 其他标签转为span或p（取决于是否是块级元素）
                    self._convert_to_allowed_tag(tag)

    def _convert_to_allowed_tag(self, tag: Tag):
        """
        将不允许的标签转换为允许的标签

        Args:
            tag: 标签对象
        """
        # 判断是否是块级元素
        block_elements = {"div", "section", "article", "header", "footer", "nav"}
        inline_elements = {"span", "a", "strong", "em", "b", "i", "u", "code"}

        if tag.name in block_elements:
            # 块级元素转为section或p
            new_tag = soup.new_tag("section")
            new_tag.attrs = tag.attrs.copy()
            tag.wrap(new_tag)
            tag.unwrap()
        elif tag.name in inline_elements:
            # 行内元素转为span
            tag.name = "span"
        else:
            # 其他情况转为p
            tag.name = "p"

        self.stats["removed_tags"] += 1

    def _process_styles(self, soup: BeautifulSoup):
        """
        处理样式，确保所有样式都是内联且符合白名单

        Args:
            soup: BeautifulSoup对象
        """
        # 移除所有style标签
        for style_tag in soup.find_all("style"):
            style_tag.decompose()
            self.stats["removed_styles"] += 1

        # 处理每个标签的style属性
        for tag in soup.find_all(True):
            if tag.has_attr("style"):
                cleaned_style = self._clean_style(tag["style"])
                if cleaned_style:
                    tag["style"] = cleaned_style
                else:
                    del tag["style"]

    def _clean_style(self, style: str) -> str:
        """
        清理CSS样式，只保留白名单内的属性

        Args:
            style: 原始样式字符串

        Returns:
            str: 清理后的样式字符串
        """
        if not style:
            return ""

        # 解析样式
        styles = {}
        for part in style.split(";"):
            part = part.strip()
            if ":" in part:
                prop, value = part.split(":", 1)
                prop = prop.strip().lower()
                value = value.strip()

                # 检查是否是允许的属性
                if prop in self.ALLOWED_CSS_PROPERTIES:
                    styles[prop] = value
                elif prop in self.FORBIDDEN_CSS_PROPERTIES:
                    self.stats["removed_styles"] += 1

        # 重新构建样式字符串
        return "; ".join([f"{k}: {v}" for k, v in styles.items()])

    def _fix_code_blocks(self, soup: BeautifulSoup):
        """
        修复代码块，处理空格和换行符

        Args:
            soup: BeautifulSoup对象
        """
        for pre in soup.find_all("pre"):
            code = pre.find("code")
            if code:
                # 获取代码文本
                code_text = code.get_text()

                # 处理缩进：将连续空格替换为\u00A0
                # 保留每行开头的2个空格作为缩进
                lines = code_text.split("\n")
                processed_lines = []
                for line in lines:
                    # 计算行首空格数
                    indent_match = re.match(r"^(\s+)", line)
                    if indent_match:
                        indent = indent_match.group(1)
                        # 将空格替换为\u00A0
                        nbsp_indent = "\u00A0" * len(indent)
                        line = nbsp_indent + line[len(indent) :]
                    processed_lines.append(line)

                # 处理换行符
                processed_code = "\n".join(processed_lines)

                # 更新code标签内容
                code.string = processed_code
                self.stats["fixed_code_blocks"] += 1

    def _process_images(self, soup: BeautifulSoup):
        """
        处理图片标签，确保符合微信规范

        Args:
            soup: BeautifulSoup对象
        """
        for img in soup.find_all("img"):
            # 确保有max-width样式
            style = img.get("style", "")
            if "max-width" not in style.lower():
                style = f"{style}; max-width: 100%; height: auto;" if style else "max-width: 100%; height: auto;"
                img["style"] = style

            # 移除事件属性
            for attr in list(img.attrs):
                if attr.startswith("on"):
                    del img[attr]

    def _process_links(self, soup: BeautifulSoup):
        """
        处理链接标签

        Args:
            soup: BeautifulSoup对象
        """
        for a in soup.find_all("a"):
            # 移除id属性（微信不支持锚点）
            if a.has_attr("id"):
                del a["id"]

            # 移除事件属性
            for attr in list(a.attrs):
                if attr.startswith("on"):
                    del a[attr]

            # 确保有target属性
            if not a.has_attr("target"):
                a["target"] = "_blank"

    def _remove_forbidden_attributes(self, soup: BeautifulSoup):
        """
        移除禁止的属性

        Args:
            soup: BeautifulSoup对象
        """
        forbidden_attrs = {"id", "class", "onclick", "onload", "onerror", "onmouseover"}

        for tag in soup.find_all(True):
            for attr in forbidden_attrs:
                if tag.has_attr(attr):
                    del tag[attr]

    def validate_html(self, html: str) -> tuple[bool, List[str]]:
        """
        验证HTML是否符合微信规范

        Args:
            html: HTML内容

        Returns:
            tuple: (是否通过验证, 错误信息列表)
        """
        errors = []

        try:
            soup = BeautifulSoup(html, "lxml")

            # 检查禁用的标签
            for tag in soup.find_all(["script", "style", "iframe"]):
                errors.append(f"发现禁用标签: <{tag.name}>")

            # 检查非内联样式
            if soup.find("style"):
                errors.append("发现<style>标签，所有样式必须是内联的")

            # 检查禁用的CSS属性
            for tag in soup.find_all(style=True):
                style = tag["style"]
                for prop in self.FORBIDDEN_CSS_PROPERTIES:
                    if prop in style.lower():
                        errors.append(f"发现禁用的CSS属性: {prop}")

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"验证失败: {str(e)}"]


def adapt_to_wechat(html: str) -> str:
    """
    适配HTML到微信规范的便捷函数

    Args:
        html: 原始HTML

    Returns:
        str: 适配后的HTML
    """
    adapter = WeChatAdapter()
    return adapter.adapt(html)


def validate_wechat_html(html: str) -> tuple[bool, List[str]]:
    """
    验证HTML是否符合微信规范的便捷函数

    Args:
        html: HTML内容

    Returns:
        tuple: (是否通过验证, 错误信息列表)
    """
    adapter = WeChatAdapter()
    return adapter.validate_html(html)
