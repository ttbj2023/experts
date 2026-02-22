"""
将 Markdown 转换为 Demis Hassabis 风格的 HTML
"""
import re
import sys
from pathlib import Path
import markdown
from bs4 import BeautifulSoup


def convert_to_demis_style(markdown_file: str, output_file: str = None):
    """
    转换 Markdown 到 Demis Hassabis 风格

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
    md = markdown.Markdown(extensions=["extra", "nl2br", "sane_lists"])
    html = md.convert(md_content)

    # 处理章节标题 - 应用 Demis Hassabis 风格
    soup = BeautifulSoup(html, "lxml")

    # 移除开头的 h1 标题（因为已经有主标题了）
    first_h1 = soup.find("h1")
    if first_h1:
        first_h1.decompose()

    # 查找所有 h2 标签并转换为 Demis Hassabis 风格
    section_number = 0
    for h2 in soup.find_all("h2"):
        section_number += 1
        section_title = h2.get_text().strip()

        # 创建 Demis Hassabis 风格的章节标题
        section_html = f"""
        <section style="width: 100%; display: flex; flex-direction: column; margin: 32px 0;">
            <section style="text-align: center;">
                <section style="font-weight: bold; font-size: 30px; color: #004080; line-height: 42px; text-shadow: 2px 2px 0px #FFDF21; word-break: break-word; font-family: Futura-Medium;">
                    {section_number:02d}
                </section>
            </section>
            <section style="align-self: center; background: #004080; transform: skewX(-7deg); padding: 4px 16px 3px 16px; margin: 0 0 26px 0;">
                <section style="transform: skewX(7deg);">
                    <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px; word-break: break-word; font-family: Optima-Regular, PingFangTC-light;">
                        {section_title}
                    </section>
                </section>
            </section>
        </section>
        """

        # 替换原始 h2 标签
        new_section = BeautifulSoup(section_html, "lxml")
        h2.replace_with(new_section)

    # 处理段落 - 添加样式
    for p in soup.find_all("p"):
        if not p.get("style"):
            p["style"] = "font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px; letter-spacing: 1px; font-family: Optima-Regular, PingFangTC-light;"

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
<section style="padding: 0px 8px; font-family: Optima-Regular, PingFangTC-light;">
  <!-- 开篇引用框 -->
  <section style="width: 100%; padding: 0px 16px;">
    <section style="width: 100%;">
      <section style="width: 100%; text-align: left; background: rgb(237, 237, 237); padding: 16px 14px 17px 16px;">
        <p style="font-size: 14px; color: rgba(0, 0, 0, 0.65); line-height: 26px; word-break: break-word; font-family: Futura-Medium;">
          {summary if summary else '本文探讨人工智能发展的关键问题，分析AGI的未来路径。'}
        </p>
      </section>
    </section>
  </section>

  <!-- 主标题 -->
  <h1 style="font-size: 30px; color: #004080; line-height: 42px; text-shadow: 2px 2px 0px #FFDF21; word-break: break-word; text-align: center; font-weight: bold; margin: 32px 0 16px; font-family: Futura-Medium;">
    {title}
  </h1>

  <!-- 作者信息 -->
  <p style="font-size: 15px; color: rgba(0, 0, 0, 0.65); line-height: 26px; text-align: center; margin: 0 0 32px;">
    {author}
  </p>

  <!-- 正文内容 -->
  <div style="font-size: 15px; margin-bottom: 16px; color: rgb(51, 51, 51); margin-top: 16px; letter-spacing: 1px; font-family: Optima-Regular, PingFangTC-light;">
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/convert_demis_style.py <markdown_file> [output_file]")
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_to_demis_style(markdown_file, output_file)
