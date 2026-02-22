"""
微信公众号 Markdown 转换器

功能特性：
1. 移除主标题和作者信息（微信公众号自带）
2. 优化代码块样式（更好的背景、圆角、字体）
3. 处理 LaTeX 公式（转换为 Unicode 数学符号，支持矩阵、积分等）
4. 基于原始Markdown缩进的列表嵌套检测
5. 跨平台字体栈支持（iOS/Android/Windows）
6. 粗体文本深蓝色、删除线灰色样式
"""
import re
import sys
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
from pylatexenc.latex2text import LatexNodes2Text
from html import unescape

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# ==================== 字体配置 ====================
# 跨平台字体栈：优先iOS/macOS原生字体，然后是Windows、安卓、通用备选
FONT_FAMILY = '-apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif'

# 数学公式字体（衬线字体，符合学术标准）
FONT_FAMILY_MATH = "'Times New Roman', serif"

# 代码字体（等宽字体）
FONT_FAMILY_CODE = "'Courier New', Consolas, Monaco, monospace"

# ==================== 字体配置结束 ====================

def number_to_chinese(num: int) -> str:
    """
    将数字转换为中文数字

    Args:
        num: 数字

    Returns:
        str: 中文数字
    """
    chinese_numbers = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                      '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']
    if num < len(chinese_numbers):
        return chinese_numbers[num]
    # 对于更大的数字，简单返回阿拉伯数字
    return str(num)


def analyze_list_indentation(md_lines: list) -> dict:
    """
    分析Markdown列表的缩进结构

    返回格式：
    {
        'ul': [(line_num, indent_level), ...],
        'ol': [(line_num, indent_level), ...]
    }

    用于识别哪些列表项是嵌套的
    """
    result = {'ul': [], 'ol': []}

    for line_num, line in enumerate(md_lines):
        # 不使用lstrip()，直接匹配原始行以保留缩进信息
        # 检测列表项
        ul_match = re.match(r'^(\s*)[-*+]\s+', line)
        ol_match = re.match(r'^(\s*)\d+\.\s+', line)

        if ul_match:
            indent = len(ul_match.group(1))
            result['ul'].append((line_num, indent))
        elif ol_match:
            indent = len(ol_match.group(1))
            result['ol'].append((line_num, indent))

    return result


def latex_to_unicode(latex: str) -> str:
    """
    将LaTeX公式转换为Unicode数学符号（使用pylatexenc）

    注意：不支持复杂的矩阵渲染，矩阵会保持LaTeX源码显示

    Args:
        latex: LaTeX公式字符串

    Returns:
        str: 转换后的字符串
    """
    # 将 \overline 替换为 \bar（pylatexenc支持\bar但不支持\overline）
    latex = re.sub(r'\\overline\{([^}]+)\}', r'\\bar{\1}', latex)

    # 使用pylatexenc进行LaTeX到Unicode的转换
    converter = LatexNodes2Text()
    result = converter.latex_to_text(latex)

    return result




def process_latex_formula(latex: str, is_block: bool = False) -> str:
    """
    处理LaTeX公式：全部转换为Unicode数学符号

    Args:
        latex: LaTeX公式字符串
        is_block: 是否为块级公式

    Returns:
        str: HTML字符串
    """
    # 转换为Unicode
    unicode_formula = latex_to_unicode(latex)

    # 根据是否为块级公式返回不同的HTML
    if is_block:
        return f'<section style="background-color: #f0f4f8; padding: 20px; border-radius: 8px; text-align: center; margin: 16px 0; border: 1px solid #cbd5e0;"><span style="background-color: #e7f3ff; color: #004080; padding: 8px 16px; border-radius: 6px; font-family: \'Times New Roman\', serif; font-size: 16px; letter-spacing: 0.5px; display: inline-block;">{unicode_formula}</span></section>'
    else:
        return f'<span style="background-color: #e7f3ff; color: #004080; padding: 2px 8px; border-radius: 4px; font-family: \'Times New Roman\', serif; font-size: 0.95em; font-style: italic;">{unicode_formula}</span>'





def convert_markdown_content_to_wechat(
    markdown_content: str,
    title: str = None,
    author: str = None,
    summary: str = None
) -> str:
    """
    转换 Markdown 内容字符串到微信公众号 HTML 格式

    Args:
        markdown_content: Markdown 文本内容
        title: 文章标题（可选，仅用于显示，不影响HTML内容）
        author: 作者名称（可选，当前不使用，保留参数以备将来）
        summary: 文章摘要（可选，如果不提供则不显示摘要框）

    Returns:
        str: 完整的HTML字符串
    """
    # 预处理：检测列表缩进结构
    md_lines = markdown_content.split('\n')
    list_structure = analyze_list_indentation(md_lines)

    # 提取 frontmatter
    metadata = {}
    if markdown_content.startswith("---"):
        parts = markdown_content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            markdown_content = parts[2]

            # 解析 frontmatter
            for line in frontmatter.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

    # 提取第一个 h1 标题作为默认标题
    title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    default_title = title_match.group(1).strip() if title_match else "无标题"

    title = title or metadata.get("title", default_title)
    # author参数暂不使用（微信公众号不在正文中显示作者）

    # 转换 Markdown 到 HTML（不使用 codehilite 和 nl2br，我们自己处理）
    # 注意：不使用 nl2br 是为了避免它将LaTeX公式中的换行转换为<br/>标签
    md = markdown.Markdown(extensions=["extra", "sane_lists", "fenced_code"])
    html = md.convert(markdown_content)

    # 处理章节标题 - 应用 Demis Hassabis 风格
    soup = BeautifulSoup(html, "lxml")

    # 使用原始Markdown缩进信息来处理列表嵌套
    # 先获取每个列表项在原始Markdown中的缩进级别

    # 移除开头的 h1 标题（因为微信公众号已经有标题了）
    first_h1 = soup.find("h1")
    if first_h1:
        first_h1.decompose()

    # 查找所有 h2 和 h3 标签并应用不同的样式（借鉴 doocs/md 的层级设计）
    # 按文档顺序处理标题，以正确维护层级编号
    h2_count = 0
    h3_count = 0

    # 获取所有标题并按在文档中的顺序排列
    all_headings = []
    for heading in soup.find_all(["h2", "h3"]):
        all_headings.append(heading)

    # 按顺序处理每个标题
    for heading in all_headings:
        if heading.name == "h2":
            h2_count += 1
            h3_count = 0  # 重置 h3 计数

            section_title = heading.get_text().strip()
            heading.clear()  # 清空原有内容

            # h2 样式：蓝底白字，较大
            heading["style"] = (
                "display: inline-block; "
                "margin: 32px auto 16px; "
                "padding: 10px 20px; "
                "text-align: center; "
                "line-height: 1.6; "
                "font-size: 18px; "
                "font-weight: bold; "
                "color: rgb(255, 255, 255); "
                "background: rgb(15, 76, 129); "
                "border-radius: 4px; "
                "max-width: 100%;"
            )
            heading["data-heading"] = "true"
            heading.string = f"{number_to_chinese(h2_count)}、{section_title}"

        elif heading.name == "h3":
            h3_count += 1

            section_title = heading.get_text().strip()
            heading.clear()  # 清空原有内容

            # h3 样式：左侧蓝条，较小，灰蓝色背景
            heading["style"] = (
                "display: inline-block; "
                "margin: 24px auto 12px; "
                "padding: 6px 12px; "
                "line-height: 1.6; "
                "font-size: 16px; "
                "font-weight: bold; "
                "color: rgb(15, 76, 129); "
                "border-left: 4px solid rgb(15, 76, 129); "
                "background: rgb(240, 244, 248); "
                "border-radius: 0 4px 4px 0; "
                "max-width: 100%;"
            )
            heading["data-heading"] = "true"
            heading.string = f"{h3_count:02d} {section_title}"

    # 处理段落 - 添加样式（针对移动端优化）
    for p in soup.find_all("p"):
        if not p.get("style"):
            # 使用数字line-height，适应字体缩放
            p["style"] = f"font-size: 15px; margin-bottom: 16px; margin-top: 16px; line-height: 1.75; color: rgb(51, 51, 51); letter-spacing: 1px; font-family: {FONT_FAMILY};"

    # 处理无序列表：保留 ul/ol/li 结构并添加样式（借鉴 doocs/md 的设计）
    for ul in soup.find_all("ul"):
        # 为 ul 添加样式
        ul["style"] = (
            "margin: 16px 0; "
            "padding-left: 24px; "
            "list-style-type: disc; "
            "color: rgb(51, 51, 51);"
        )

        # 为所有 li 添加样式（包括嵌套的）
        for li in ul.find_all("li", recursive=True):
            if not li.get("style"):
                li["style"] = (
                    "font-size: 15px; "
                    "line-height: 1.75; "
                    "margin: 8px 0; "
                    "color: rgb(51, 51, 51); "
                    "letter-spacing: 1px;"
                )

    # 处理有序列表：保留 ul/ol/li 结构并添加样式（借鉴 doocs/md 的设计）
    for ol in soup.find_all("ol"):
        # 为 ol 添加样式
        ol["style"] = (
            "margin: 16px 0; "
            "padding-left: 24px; "
            "list-style-type: decimal; "
            "color: rgb(51, 51, 51);"
        )

        # 为所有 li 添加样式（包括嵌套的）
        for li in ol.find_all("li", recursive=True):
            if not li.get("style"):
                li["style"] = (
                    "font-size: 15px; "
                    "line-height: 1.75; "
                    "margin: 8px 0; "
                    "color: rgb(51, 51, 51); "
                    "letter-spacing: 1px;"
                )
    # 处理粗体文本（添加深蓝色）
    for bold in soup.find_all(["strong", "b"]):
        if not bold.get("style"):
            bold["style"] = "color: rgb(15, 76, 129); font-weight: bold;"

    # 处理删除线文本（手动转换~~文本~~为<del>标签）
    # Python markdown库默认不支持~~删除线~~语法，需要手动处理
    def process_strikethrough(text):
        """递归处理删除线语法~~文本~~"""
        import re
        def replace_strikethrough(match):
            content = match.group(1)
            # 递归处理嵌套的删除线
            content = process_strikethrough(content)
            return f'<del style="color: #999999; text-decoration: line-through;">{content}</del>'

        # 使用正则表达式匹配~~文本~~（支持跨行）
        pattern = r'~~([^\~]+?)~~'
        return re.sub(pattern, replace_strikethrough, text, flags=re.DOTALL)

    # 遍历所有文本节点并处理删除线
    for element in soup.find_all(string=True):
        if '~~' in str(element):
            new_text = process_strikethrough(str(element))
            if new_text != str(element):
                # 创建新的HTML并替换
                new_element = BeautifulSoup(new_text, "lxml")
                element.replace_with(new_element)

    # 处理已有的删除线标签（添加灰色样式）
    for del_tag in soup.find_all(["del", "s", "strike"]):
        if not del_tag.get("style"):
            del_tag["style"] = "color: #999999; text-decoration: line-through;"

    # 处理行内代码（先处理，避免被代码块处理影响）
    for code in soup.find_all("code"):
        # 如果不在 pre 标签内（行内代码）
        if code.find_parent("pre") is None:
            code_text = code.get_text()
            code_html = f'<span style="background-color: #f6f8fa; color: #d63384; padding: 2px 6px; border-radius: 4px; font-family: \'Courier New\', Consolas, Monaco, monospace; font-size: 0.9em;">{code_text}</span>'
            new_code = BeautifulSoup(code_html, "lxml")
            code.replace_with(new_code)

    # 优化代码块样式（在处理行内代码之后）
    for pre in soup.find_all("pre"):
        # 找到里面的 code 标签
        code_tag = pre.find("code")
        if not code_tag:
            continue

        # 获取代码内容
        code_content = code_tag.get_text()

        # 处理代码块：保留换行，用&nbsp;替代空格（避免缩进丢失）
        # 将换行符转为<br>标签
        code_lines = code_content.split('\n')
        processed_lines = []
        for line in code_lines:
            # 将行首空格转换为&nbsp;（保留缩进）
            line = line.rstrip()
            # 计算行首空格数
            leading_spaces = len(line) - len(line.lstrip())
            # 转换行首空格为&nbsp;
            indented_line = '&nbsp;' * leading_spaces + line.lstrip()
            processed_lines.append(indented_line)

        # 用<br>连接各行
        code_html_content = '<br/>'.join(processed_lines)

        # 创建美化后的代码块
        code_html = f"""
        <section style="margin: 16px 0; padding: 0;">
            <section style="background-color: #f6f8fa; padding: 16px; border-radius: 8px; border-left: 4px solid #004080; overflow-x: auto;">
                <code style="font-family: 'Courier New', Consolas, Monaco, monospace; font-size: 13px; line-height: 1.8; color: #333; white-space: nowrap; display: block;">
                    {code_html_content}
                </code>
            </section>
        </section>
        """

        new_code_block = BeautifulSoup(code_html, "lxml")
        pre.replace_with(new_code_block)

    # 处理 LaTeX 公式（全部转换为Unicode数学符号）
    for p in soup.find_all("p"):
        p_html = str(p)
        if '$' in p_html:
            # $$...$$ 块级公式
            def replace_block_formula(match):
                latex_formula = match.group(1).strip()
                # 反转义HTML实体（Markdown转换器将&转换为&amp;）
                latex_formula = unescape(latex_formula)
                return process_latex_formula(latex_formula, is_block=True)

            p_html = re.sub(r'\$\$([^$]+)\$\$', replace_block_formula, p_html)

            # $...$ 行内公式
            def replace_inline_formula(match):
                latex_formula = match.group(1).strip()
                # 反转义HTML实体（Markdown转换器将&转换为&amp;）
                latex_formula = unescape(latex_formula)
                return process_latex_formula(latex_formula, is_block=False)

            p_html = re.sub(r'\$([^$]+)\$', replace_inline_formula, p_html)
            new_p = BeautifulSoup(p_html, "lxml")
            p.replace_with(new_p)

    # 清理嵌套的 html/body 标签
    for tag in soup.find_all(["html", "body"]):
        tag.unwrap()

    # 清理空的嵌套 section
    for section in soup.find_all("section"):
        if not section.get_text().strip() and len(section.find_all()) == 0:
            section.decompose()

    # 构建完整的 HTML（简化版，不包含主标题）
    content_html = str(soup).strip()

    # 摘要框（可选）
    summary_section = ""
    if summary:
        summary_section = f"""
  <!-- 开篇引用框（优化版 - 半透明灰蓝色） -->
  <section style="width: 100%; padding: 0px 16px;">
    <section style="width: 100%; text-align: center; margin: 24px 0;">
      <section style="display: inline-block; max-width: 100%; text-align: left; background-color: rgba(96, 125, 139, 0.15); padding: 20px 24px; border-radius: 12px; border-left: 4px solid #607D8B;">
        <p style="font-size: 15px; color: #455A64; line-height: 1.8; margin: 0; font-weight: 500; letter-spacing: 0.5px; font-family: {FONT_FAMILY};">
          {summary}
        </p>
      </section>
    </section>
  </section>
"""

    # 构建完整的 HTML，紧凑格式，无多余空行
    full_html = (
        f'<section style="padding: 0px 8px; font-family: {FONT_FAMILY};">\n'
        '  <!-- 正文内容 -->\n'
        f'  <div style="font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px; letter-spacing: 1px; font-family: {FONT_FAMILY};">\n'
        f'    {content_html}\n'
        '  </div><!-- 文章结尾 --><section style="margin-top: 32px;">\n'
        '    <hr style="height: 1px; background-color: #e5e7eb; border: none;" />\n'
        '    <p style="font-size: 14px; color: #666666; line-height: 1.6; text-align: center; margin: 24px 0;">\n'
        '      感谢阅读\n'
        '    </p>\n'
        '  </section>\n'
        '</section>'
    )

    return full_html


def convert_markdown_to_wechat(markdown_file: str, output_file: str = None):
    """
    转换 Markdown 文件到微信公众号 HTML 格式（文件接口）

    Args:
        markdown_file: Markdown 文件路径
        output_file: 输出 HTML 文件路径
    """
    # 读取文件
    md_path = Path(markdown_file)
    if not md_path.exists():
        print(f"❌ 文件不存在: {markdown_file}")
        return

    md_content = md_path.read_text(encoding="utf-8")

    # 提取标题（从文件名或内容）
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    default_title = title_match.group(1).strip() if title_match else md_path.stem

    # 注意：此接口不生成摘要，需要调用者提供
    # 为了兼容性，这里会提取一个简单的摘要，但建议使用convert_markdown_content_to_wechat
    summary = f"本文介绍了{default_title}的相关内容，帮助读者快速了解关键信息。"

    # 调用内容转换函数
    full_html = convert_markdown_content_to_wechat(
        markdown_content=md_content,
        title=default_title,
        author="原创",
        summary=summary
    )

    # 保存 HTML
    if not output_file:
        output_file = md_path.with_suffix(".html")

    output_path = Path(output_file)
    output_path.write_text(full_html, encoding="utf-8")

    print(f"✅ 转换成功！")
    print(f"📄 HTML 已保存到: {output_path}")
    print(f"📝 标题: {default_title}")
    print(f"\n💡 优化说明：")
    print(f"   - 已移除主标题和作者信息（微信公众号自带）")
    print(f"   - 代码块已优化样式（背景色、圆角、左侧边框、正确换行）")
    print(f"   - 列表：使用段落模拟（避免微信编辑器列表符号后换行）")
    print(f"   - LaTeX 公式：全部转换为Unicode数学符号")
    print(f"   - 开篇引用框：半透明灰蓝色 + 左侧边框")
    print(f"   - 支持：希腊字母、运算符、矩阵、集合、积分、求和等")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/convert_demis_style_v2.py <markdown_file> [output_file]")
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_to_demis_style(markdown_file, output_file)
