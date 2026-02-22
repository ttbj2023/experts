"""
将 Markdown 转换为简约现代风格（类似"孤胆英雄"、"为什么中国6G的建设静悄悄？"）

特点：
1. h2标题：深蓝色背景，白色文字，居中显示
2. h3标题：左侧蓝色竖线，无背景
3. 正文：两端对齐，宽松行高
4. 强调文字：深蓝色加粗
5. 分隔线：灰色细线
"""
import re
import sys
from pathlib import Path
import markdown
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def convert_to_simple_style(markdown_file: str, output_file: str = None):
    """
    转换 Markdown 到简约现代风格

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

    # 转换 Markdown 到 HTML
    md = markdown.Markdown(extensions=["extra", "sane_lists", "fenced_code"])
    html = md.convert(md_content)

    # 处理HTML
    soup = BeautifulSoup(html, "lxml")

    # 移除开头的 h1 标题（因为微信公众号已经有标题了）
    first_h1 = soup.find("h1")
    if first_h1:
        first_h1.decompose()

    # 处理 h2 标题 - 深蓝色背景，白色文字，居中
    for h2 in soup.find_all("h2"):
        section_title = h2.get_text().strip()

        h2['style'] = """display: table; margin: 4em auto 2em; text-align: center; line-height: 1.75; font-size: 16.8px; font-weight: bold; padding: 0px 0.2em; color: rgb(255, 255, 255); background: rgb(15, 76, 129);"""

    # 处理 h3 标题 - 左侧蓝色竖线
    for h3 in soup.find_all("h3"):
        h3['style'] = """border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; margin-bottom: 0.5em; font-size: 16px; font-weight: bold; color: rgb(0, 0, 0);"""

    # 处理段落 - 两端对齐，宽松行高
    for p in soup.find_all("p"):
        if not p.get("style"):
            p['style'] = """margin: 1.5em 8px; text-align: justify; line-height: 1.75; font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif; font-size: 14px; letter-spacing: 0.1em; color: rgb(63, 63, 63);"""

    # 处理引用块（blockquote）
    for blockquote in soup.find_all("blockquote"):
        blockquote['style'] = """border-left: 4px solid rgb(15, 76, 129); margin: 1.5em 0;"""
        # 为blockquote内的p添加样式
        for p in blockquote.find_all("p"):
            p['style'] = """margin: 0px; text-align: left; line-height: 1.75; font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif; font-size: 1em; display: block; letter-spacing: 0.1em; color: rgb(63, 63, 63);"""

    # 处理强调文字（strong）
    for strong in soup.find_all("strong"):
        strong['style'] = """font-weight: bold; color: rgb(15, 76, 129); font-size: inherit;"""

    # 处理分隔线（hr）
    for hr in soup.find_all("hr"):
        hr['style'] = """border-width: 2px 0px 0px; border-style: solid; border-color: rgba(0, 0, 0, 0.1); height: 0.4em; color: inherit; margin: 1.5em 0px; transform: scale(1, 0.5);"""

    # 处理列表
    for ul in soup.find_all("ul"):
        ul['style'] = """list-style: circle; margin: 0px; padding: 0px 0px 0px 1em; text-align: left; line-height: 1.75; font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif; font-size: 14px; color: rgb(63, 63, 63);"""
        for li in ul.find_all("li"):
            li['style'] = """text-indent: -1em; display: block; margin: 0.2em 8px;"""

    for ol in soup.find_all("ol"):
        ol['style'] = """margin: 0px; padding: 0px 0px 0px 1.8em; text-align: left; line-height: 1.75; font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif; font-size: 14px; color: rgb(63, 63, 63);"""
        for li in ol.find_all("li"):
            li['style'] = """margin: 0.2em 8px;"""

    # 处理代码块
    for pre in soup.find_all("pre"):
        code_tag = pre.find("code")
        if not code_tag:
            continue

        code_content = code_tag.get_text()

        # 处理代码块：保留换行，用&nbsp;替代空格
        code_lines = code_content.split('\n')
        processed_lines = []
        for line in code_lines:
            line = line.rstrip()
            leading_spaces = len(line) - len(line.lstrip())
            indented_line = '&nbsp;' * leading_spaces + line.lstrip()
            processed_lines.append(indented_line)

        code_html_content = '<br/>'.join(processed_lines)

        code_html = f"""
        <section style="margin: 16px 0; padding: 0;">
            <section style="background-color: #f6f8fa; padding: 16px; border-radius: 8px; border-left: 4px solid rgb(15, 76, 129); overflow-x: auto;">
                <code style="font-family: 'Courier New', Consolas, Monaco, monospace; font-size: 13px; line-height: 1.8; color: #333; white-space: nowrap; display: block;">
                    {code_html_content}
                </code>
            </section>
        </section>
        """

        new_code_block = BeautifulSoup(code_html, "lxml")
        pre.replace_with(new_code_block)

    # 处理行内代码
    for code in soup.find_all("code"):
        if code.find_parent("pre") is None:
            code_text = code.get_text()
            code_html = f'<span style="background-color: #f6f8fa; color: #d63384; padding: 2px 6px; border-radius: 4px; font-family: \'Courier New\', Consolas, Monaco, monospace; font-size: 0.9em;">{code_text}</span>'
            new_code = BeautifulSoup(code_html, "lxml")
            code.replace_with(new_code)

    # 清理嵌套的 html/body 标签
    for tag in soup.find_all(["html", "body"]):
        tag.unwrap()

    # 清理空的嵌套 section
    for section in soup.find_all("section"):
        if not section.get_text().strip() and len(section.find_all()) == 0:
            section.decompose()

    # 构建完整的 HTML
    content_html = str(soup)

    full_html = f"""
<section style="padding: 0px 8px; font-family: -apple-system-font, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif;">
  <!-- 开篇引用框 -->
  <section style="width: 100%; padding: 0px 16px;">
    <section style="width: 100%; text-align: center; margin: 24px 0;">
      <section style="display: inline-block; max-width: 100%; text-align: left; background-color: rgba(96, 125, 139, 0.15); padding: 20px 24px; border-radius: 12px; border-left: 4px solid #607D8B;">
        <p style="font-size: 15px; color: #455A64; line-height: 1.8; margin: 0; font-weight: 500; letter-spacing: 0.5px;">
          {summary}
        </p>
      </section>
    </section>
  </section>

  <!-- 正文内容 -->
  <div style="font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px;">
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
    print(f"\n💡 风格说明：")
    print(f"   - 简约现代风格（类似'孤胆英雄'、'为什么中国6G的建设静悄悄？'）")
    print(f"   - h2: 深蓝色背景 + 白色文字 + 居中显示")
    print(f"   - h3: 左侧蓝色竖线")
    print(f"   - 正文: 两端对齐 + 宽松行高 (1.75)")
    print(f"   - 强调: 深蓝色加粗")
    print(f"   - 分隔线: 灰色细线")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/convert_simple_style.py <markdown_file> [output_file]")
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_to_simple_style(markdown_file, output_file)
