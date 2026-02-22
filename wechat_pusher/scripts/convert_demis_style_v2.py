"""
将 Markdown 转换为 Demis Hassabis 风格的 HTML（优化版）

优化内容：
1. 移除主标题和作者信息（微信公众号自带）
2. 优化代码块样式（更好的背景、圆角、字体）
3. 处理 LaTeX 公式（转换为 Unicode 数学符号，支持矩阵、积分等）
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





def convert_to_demis_style(markdown_file: str, output_file: str = None):
    """
    转换 Markdown 到 Demis Hassabis 风格（优化版）

    Args:
        markdown_file: Markdown 文件路径
        output_file: 输出 HTML 文件路径
    """
    # 读取 Markdown 文件
    md_path = Path(markdown_file)
    if not md_path.exists():
        print(f"❌ 文件不存在: {markdown_file}")
        return

    md_content = md_path.read_text(encoding="utf-8")

    # 预处理：检测列表缩进结构
    md_lines = md_content.split('\n')
    list_structure = analyze_list_indentation(md_lines)

    # 提取 frontmatter
    metadata = {}
    if md_content.startswith("---"):
        parts = md_content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            md_content = parts[2]

            # 解析 frontmatter
            for line in frontmatter.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

    # 提取第一个 h1 标题作为默认标题
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    default_title = title_match.group(1).strip() if title_match else md_path.stem

    title = metadata.get("title", default_title)
    author = metadata.get("author", "原创")

    # 生成摘要（从第一段提取或使用默认）
    summary = metadata.get("summary", "")
    if not summary:
        # 尝试提取第一段文字
        first_para_match = re.search(r'^(?!#)(.+)$', md_content, re.MULTILINE)
        if first_para_match:
            first_para = first_para_match.group(1).strip()
            # 移除 Markdown 格式
            summary = re.sub(r'[*_`~#]', '', first_para)
            if len(summary) > 100:
                summary = summary[:97] + "..."

    # 如果还是没有摘要，使用默认
    if not summary:
        summary = f"本文介绍了{title}的相关内容，帮助读者快速了解关键信息。"

    # 转换 Markdown 到 HTML（不使用 codehilite 和 nl2br，我们自己处理）
    # 注意：不使用 nl2br 是为了避免它将LaTeX公式中的换行转换为<br/>标签
    md = markdown.Markdown(extensions=["extra", "sane_lists", "fenced_code"])
    html = md.convert(md_content)

    # 处理章节标题 - 应用 Demis Hassabis 风格
    soup = BeautifulSoup(html, "lxml")

    # 使用原始Markdown缩进信息来处理列表嵌套
    # 先获取每个列表项在原始Markdown中的缩进级别

    # 移除开头的 h1 标题（因为微信公众号已经有标题了）
    first_h1 = soup.find("h1")
    if first_h1:
        first_h1.decompose()

    # 查找所有 h2 标签并转换为混合风格
    # 使用简约风格的标题样式（蓝底白字，编号在内），但保留章节编号
    section_number = 0
    for h2 in soup.find_all("h2"):
        section_number += 1
        section_title = h2.get_text().strip()

        # 创建混合风格标题：简约风格的h2（蓝底白字）+ 保留Demis风格的特性
        # 格式：01 标题文本（蓝色背景，白色文字）
        section_html = f"""
        <h2 style="display: table; margin: 32px auto; padding: 0px 0.2em; text-align: center; line-height: 1.75; font-size: 16.8px; font-weight: bold; color: rgb(255, 255, 255); background: rgb(15, 76, 129); transform: skewX(-7deg);">
            <section style="transform: skewX(7deg); word-break: break-word; font-family: {FONT_FAMILY}; white-space: nowrap;">
                {section_number:02d} {section_title}
            </section>
        </h2>
        """

        # 替换原始 h2 标签
        new_section = BeautifulSoup(section_html, "lxml")
        h2.replace_with(new_section)

    # 处理段落 - 添加样式（针对移动端优化）
    for p in soup.find_all("p"):
        if not p.get("style"):
            # 使用数字line-height，适应字体缩放
            p["style"] = f"font-size: 15px; margin-bottom: 14px; margin-top: 14px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"

    # 将列表转换为段落模拟（避免微信编辑器的列表符号后换行问题）
    for ul in soup.find_all("ul"):
        # 收集所有非空的li
        list_items = []
        for idx, li in enumerate(ul.find_all("li", recursive=False), 1):
            # 清理li内容末尾的空白字符（包括换行符）
            for content in li.contents:
                if hasattr(content, 'name'):
                    continue  # 跳过标签
                # 处理文本节点，移除首尾空白
                if content.strip():
                    new_text = str(content).strip()
                    content.replace_with(new_text)

            # 移除空的li标签
            if not li.get_text().strip() and len(li.find_all()) == 0:
                li.decompose()
                continue

            list_items.append((idx, li))

        # 使用缩进级别检测嵌套（基于原始Markdown结构）
        # 获取当前ul在文档中的位置，用于查找对应的Markdown源码
        nested_groups = []

        # 为每个li分配缩进级别
        item_indent_levels = []
        for idx, li in list_items:
            li_text = li.get_text().strip()

            # 尝试在原始Markdown中查找对应的行，获取缩进级别
            indent_level = 0  # 默认为0（顶级）

            # 在原始Markdown行中搜索匹配的文本
            for line_num, indent in list_structure['ul']:
                if line_num < len(md_lines):
                    md_line = md_lines[line_num].strip()
                    # 检查Markdown行是否匹配当前li的文本
                    # 移除列表符号和空格后比较
                    md_content = re.sub(r'^[-*+]\s+', '', md_line)
                    li_content_only = re.sub(r'^[-*•]\s*', '', li_text)

                    # 使用startswith匹配，因为HTML可能包含额外的标签
                    if md_content and li_content_only and md_content.startswith(li_content_only[:30]):
                        indent_level = indent
                        break

            item_indent_levels.append((idx, li, indent_level))

        # 基于缩进级别分组
        i = 0
        while i < len(item_indent_levels):
            idx, li, current_indent = item_indent_levels[i]

            # 查找后续具有更大缩进的项（子项）
            children = []
            j = i + 1
            while j < len(item_indent_levels):
                next_idx, next_li, next_indent = item_indent_levels[j]

                # 如果下一项缩进更大，则是子项
                if next_indent > current_indent:
                    children.append((next_idx, next_li))
                    j += 1
                # 如果缩进相同或更小，停止收集子项
                elif next_indent <= current_indent:
                    break

            if children:
                nested_groups.append({
                    'parent': (idx, li),
                    'children': children
                })

            i += 1

        # 替换ul为段落列表
        new_paragraphs = []
        processed_indices = set()

        # 将嵌套组映射为字典，方便查找
        group_map = {}
        for group in nested_groups:
            parent_idx, _ = group['parent']
            group_map[parent_idx] = group

        # 按顺序处理所有项
        for idx, li in list_items:
            # 检查是否是嵌套组的父项
            if idx in group_map:
                group = group_map[idx]
                parent_idx, parent_li = group['parent']
                children = group['children']

                # 标记为已处理
                processed_indices.add(parent_idx)
                for child_idx, _ in children:
                    processed_indices.add(child_idx)

                # 处理父项
                parent_content = str(parent_li).replace("<li>", "").replace("</li>", "").strip()
                p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"><span style="font-weight: bold; color: rgb(15, 76, 129); margin-right: 4px;">•</span>{parent_content}</p>'
                new_paragraphs.append(BeautifulSoup(p_html, "lxml"))

                # 处理子项（带缩进，使用不同的符号）
                for child_idx, child_li in children:
                    child_content = str(child_li).replace("<li>", "").replace("</li>", "").strip()
                    # 检测是否需要移除原始的项目符号（如果有的话）
                    child_content = re.sub(r'^[-\*•]\s*', '', child_content)
                    # 使用圆圈符号表示嵌套
                    p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY}; margin-left: 2em;"><span style="font-weight: bold; color: rgb(15, 76, 129); margin-right: 4px;">○</span>{child_content}</p>'
                    new_paragraphs.append(BeautifulSoup(p_html, "lxml"))

                # 跳过后续处理，继续下一个父项
                continue

            # 检查是否已被处理为子项
            if idx in processed_indices:
                continue

            # 获取li的内容HTML
            li_content = str(li).replace("<li>", "").replace("</li>", "")

            # 检查是否有真实的嵌套列表（HTML嵌套，非伪嵌套）
            nested_ul = li.find("ul", recursive=False)
            nested_ol = li.find("ol", recursive=False)

            if nested_ul or nested_ol:
                # 主项（包含嵌套）
                main_content = li.get_text().split("\n")[0]  # 获取第一行作为主项内容
                if not main_content.strip():
                    main_content = li.contents[0].strip() if li.contents and not hasattr(li.contents[0], 'name') else "展开"

                p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"><span style="font-weight: bold; color: rgb(15, 76, 129); margin-right: 4px;">•</span>{main_content}</p>'
                new_paragraphs.append(BeautifulSoup(p_html, "lxml"))

                # 处理嵌套列表
                if nested_ul:
                    nested_items = []
                    for nested_li in nested_ul.find_all("li", recursive=False):
                        nested_content = str(nested_li).replace("<li>", "").replace("</li>", "")
                        nested_p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY}; margin-left: 2em;"><span style="font-weight: bold; color: rgb(15, 76, 129); margin-right: 4px;">○</span>{nested_content}</p>'
                        nested_items.append(BeautifulSoup(nested_p_html, "lxml"))

                    for nested_p in nested_items:
                        new_paragraphs.append(nested_p)
                elif nested_ol:
                    nested_items = []
                    for idx, nested_li in enumerate(nested_ol.find_all("li", recursive=False), 1):
                        nested_content = str(nested_li).replace("<li>", "").replace("</li>", "")
                        nested_p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY}; margin-left: 2em;"><span style="font-weight: bold; color: rgb(15, 76, 129);">{idx}.</span> {nested_content}</p>'
                        nested_items.append(BeautifulSoup(nested_p_html, "lxml"))

                    for nested_p in nested_items:
                        new_paragraphs.append(nested_p)
            else:
                # 普通项
                p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"><span style="font-weight: bold; color: rgb(15, 76, 129); margin-right: 4px;">•</span>{li_content}</p>'
                new_paragraphs.append(BeautifulSoup(p_html, "lxml"))

        # 替换整个ul
        if new_paragraphs:
            for i, p in enumerate(new_paragraphs):
                ul.insert_before(p)
                # 在段落之间添加换行符（除了最后一个）
                if i < len(new_paragraphs) - 1:
                    ul.insert_before('\n')
            ul.decompose()

    for ol in soup.find_all("ol"):
        # 收集所有非空的li
        list_items = []
        for idx, li in enumerate(ol.find_all("li", recursive=False), 1):
            # 清理li内容末尾的空白字符（包括换行符）
            for content in li.contents:
                if hasattr(content, 'name'):
                    continue  # 跳过标签
                # 处理文本节点，移除首尾空白
                if content.strip():
                    new_text = str(content).strip()
                    content.replace_with(new_text)

            # 移除空的li标签
            if not li.get_text().strip() and len(li.find_all()) == 0:
                li.decompose()
                continue

            list_items.append((idx, li))

        # 使用缩进级别检测嵌套（基于原始Markdown结构）
        nested_groups = []

        # 为每个li分配缩进级别
        item_indent_levels = []
        for idx, li in list_items:
            li_text = li.get_text().strip()

            # 尝试在原始Markdown中查找对应的行，获取缩进级别
            indent_level = 0  # 默认为0（顶级）

            # 在原始Markdown行中搜索匹配的文本
            for line_num, indent in list_structure['ol']:
                if line_num < len(md_lines):
                    md_line = md_lines[line_num].strip()
                    # 检查Markdown行是否匹配当前li的文本
                    # 移除列表符号和空格后比较
                    md_content = re.sub(r'^\d+\.\s+', '', md_line)
                    li_content_only = re.sub(r'^\d+\.\s*', '', li_text)

                    # 使用startswith匹配，因为HTML可能包含额外的标签
                    if md_content and li_content_only and md_content.startswith(li_content_only[:30]):
                        indent_level = indent
                        break

            item_indent_levels.append((idx, li, indent_level))

        # 基于缩进级别分组
        i = 0
        while i < len(item_indent_levels):
            idx, li, current_indent = item_indent_levels[i]

            # 查找后续具有更大缩进的项（子项）
            children = []
            j = i + 1
            while j < len(item_indent_levels):
                next_idx, next_li, next_indent = item_indent_levels[j]

                # 如果下一项缩进更大，则是子项
                if next_indent > current_indent:
                    children.append((next_idx, next_li))
                    j += 1
                # 如果缩进相同或更小，停止收集子项
                elif next_indent <= current_indent:
                    break

            if children:
                nested_groups.append({
                    'parent': (idx, li),
                    'children': children
                })

            i += 1

        # 替换ol为段落列表
        new_paragraphs = []
        processed_indices = set()
        actual_idx = 1  # 实际显示的编号

        # 将嵌套组映射为字典，方便查找
        group_map = {}
        for group in nested_groups:
            parent_idx, _ = group['parent']
            group_map[parent_idx] = group

        # 按顺序处理所有项
        for idx, li in list_items:
            # 检查是否是嵌套组的父项
            if idx in group_map:
                group = group_map[idx]
                parent_idx, parent_li = group['parent']
                children = group['children']

                # 标记为已处理
                processed_indices.add(parent_idx)
                for child_idx, _ in children:
                    processed_indices.add(child_idx)

                # 处理父项
                parent_content = str(parent_li).replace("<li>", "").replace("</li>", "").strip()
                p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"><span style="font-weight: bold; color: rgb(15, 76, 129);">{actual_idx}.</span> {parent_content}</p>'
                new_paragraphs.append(BeautifulSoup(p_html, "lxml"))
                parent_display_idx = actual_idx
                actual_idx += 1

                # 处理子项（带缩进，重新编号）
                for i, (child_idx, child_li) in enumerate(children, 1):
                    child_content = str(child_li).replace("<li>", "").replace("</li>", "").strip()
                    # 检测是否需要移除原始编号（如果以"1." "2."等开头）
                    child_content = re.sub(r'^\d+\.\s*', '', child_content)
                    # 使用子编号
                    p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY}; margin-left: 2em;"><span style="font-weight: bold; color: rgb(15, 76, 129);">{parent_display_idx}.{i}</span> {child_content}</p>'
                    new_paragraphs.append(BeautifulSoup(p_html, "lxml"))

                # 跳过后续处理，继续下一个父项
                continue

            # 检查是否已被处理为子项
            if idx in processed_indices:
                continue

            # 获取li的内容HTML
            li_content = str(li).replace("<li>", "").replace("</li>", "")

            # 检查是否有嵌套列表
            nested_ul = li.find("ul", recursive=False)
            nested_ol = li.find("ol", recursive=False)

            if nested_ul or nested_ol:
                # 主项（包含嵌套）
                main_content = li.get_text().split("\n")[0]  # 获取第一行作为主项内容
                if not main_content.strip():
                    main_content = li.contents[0].strip() if li.contents and not hasattr(li.contents[0], 'name') else "展开"

                p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"><span style="font-weight: bold; color: rgb(15, 76, 129);">{actual_idx}.</span> {main_content}</p>'
                new_paragraphs.append(BeautifulSoup(p_html, "lxml"))
                parent_idx = actual_idx
                actual_idx += 1

                # 处理嵌套列表
                if nested_ul:
                    nested_items = []
                    for nested_li in nested_ul.find_all("li", recursive=False):
                        nested_content = str(nested_li).replace("<li>", "").replace("</li>", "")
                        nested_p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY}; margin-left: 2em;"><span style="font-weight: bold; color: rgb(15, 76, 129); margin-right: 4px;">•</span>{nested_content}</p>'
                        nested_items.append(BeautifulSoup(nested_p_html, "lxml"))

                    for nested_p in nested_items:
                        new_paragraphs.append(nested_p)
                elif nested_ol:
                    nested_items = []
                    for nested_idx, nested_li in enumerate(nested_ol.find_all("li", recursive=False), 1):
                        nested_content = str(nested_li).replace("<li>", "").replace("</li>", "")
                        nested_p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY}; margin-left: 2em;"><span style="font-weight: bold; color: rgb(15, 76, 129);">{parent_idx}.{nested_idx}</span> {nested_content}</p>'
                        nested_items.append(BeautifulSoup(nested_p_html, "lxml"))

                    for nested_p in nested_items:
                        new_paragraphs.append(nested_p)
            else:
                # 森测教辅题目格式：内容中包含 "A." "B." "C." "D." 或 "(1)" "(2)" 等选项
                li_text = li.get_text()

                # 检测选择题选项 (A. B. C. D. 或 A、B、C、D、)
                has_multiple_choice = re.search(r'[A-D]\.|\([A-D]\)|[A-D]、', li_text)
                # 检测步骤选项 ((1) (2) 或 1) 2))
                has_steps = re.search(r'\(\d+\)[^\)]', li_text)

                if has_multiple_choice or has_steps:
                    # 将内容按行分割
                    lines = li_text.strip().split('\n')

                    # 第一行是题目
                    if lines:
                        title_line = lines[0].strip()
                        # 移除开头的编号（如果有的话）
                        title_line = re.sub(r'^\d+\.\s*', '', title_line)
                        p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"><span style="font-weight: bold; color: rgb(15, 76, 129);">{actual_idx}.</span> {title_line}</p>'
                        new_paragraphs.append(BeautifulSoup(p_html, "lxml"))
                        actual_idx += 1

                    # 后续行是选项，每个选项单独一段
                    for line in lines[1:]:
                        line = line.strip()
                        if line:
                            # 添加缩进
                            p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY}; margin-left: 2em;">{line}</p>'
                            new_paragraphs.append(BeautifulSoup(p_html, "lxml"))
                else:
                    # 普通项
                    p_html = f'<p style="font-size: 15px; margin-bottom: 8px; margin-top: 8px; line-height: 1.6; color: rgb(51, 51, 51); letter-spacing: 0.5px; font-family: {FONT_FAMILY};"><span style="font-weight: bold; color: rgb(15, 76, 129);">{actual_idx}.</span> {li_content}</p>'
                    new_paragraphs.append(BeautifulSoup(p_html, "lxml"))
                    actual_idx += 1

        # 替换整个ol
        if new_paragraphs:
            for i, p in enumerate(new_paragraphs):
                ol.insert_before(p)
                # 在段落之间添加换行符（除了最后一个）
                if i < len(new_paragraphs) - 1:
                    ol.insert_before('\n')
            ol.decompose()

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
    content_html = str(soup)

    full_html = f"""
<section style="padding: 0px 8px; font-family: {FONT_FAMILY};">
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

  <!-- 正文内容 -->
  <div style="font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px; letter-spacing: 1px; font-family: {FONT_FAMILY};">
    {content_html}
  </div>

  <!-- 文章结尾 -->
  <section style="margin-top: 48px;">
    <hr style="height: 1px; background-color: #e5e7eb; border: none;" />
    <p style="font-size: 14px; color: #666666; line-height: 1.6; text-align: center; margin: 24px 0;">
      感谢阅读
    </p>
  </section>
</section>
    """

    # 保存 HTML
    if not output_file:
        output_file = md_path.with_suffix(".html")

    output_path = Path(output_file)
    output_path.write_text(full_html, encoding="utf-8")

    print(f"✅ 转换成功！")
    print(f"📄 HTML 已保存到: {output_path}")
    print(f"📝 标题: {title}")
    print(f"✍️  作者: {author}")
    print(f"📊 章节数: {section_number}")
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
