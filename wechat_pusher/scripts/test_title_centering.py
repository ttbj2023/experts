#!/usr/bin/env python3
"""
测试不同标题居中方案
"""
import re
import sys
from pathlib import Path
import markdown
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

# 6种不同的居中方案
CENTERING_METHODS = {
    1: """flexbox""",
    2: """fixed_width""",
    3: """inline_block""",
    4: """fit_content""",
    5: """table""",
    6: """transform""",
}

def get_title_html(section_number: int, section_title: str, method: int) -> str:
    """生成指定居中方案的标题HTML"""
    
    # 数字标题
    number_html = f"""
    <section style="font-weight: bold; font-size: 30px; color: #004080; line-height: 42px; text-shadow: 2px 2px 0px #FFDF21; word-break: break-word; font-family: Futura-Medium; text-align: center;">
        {section_number:02d}
    </section>
    """
    
    # 根据方案生成不同的标题栏HTML
    if method == 1:  # Flexbox
        bar_html = f"""
        <section style="display: flex; justify-content: center; margin-top: 8px;">
            <section style="background: #004080; transform: skewX(-7deg); padding: 4px 16px 3px 16px;">
                <section style="transform: skewX(7deg);">
                    <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px; word-break: break-word; font-family: Optima-Regular, PingFangTC-light;">
                        {section_title}
                    </section>
                </section>
            </section>
        </section>
        """
    
    elif method == 2:  # 固定宽度 + margin auto
        bar_html = f"""
        <section style="width: 200px; margin: 8px auto 0 auto;">
            <section style="background: #004080; transform: skewX(-7deg); padding: 4px 16px 3px 16px; text-align: center;">
                <section style="transform: skewX(7deg);">
                    <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px; word-break: break-word; font-family: Optima-Regular, PingFangTC-light;">
                        {section_title}
                    </section>
                </section>
            </section>
        </section>
        """
    
    elif method == 3:  # inline-block + text-align
        bar_html = f"""
        <section style="text-align: center; margin-top: 8px;">
            <section style="display: inline-block; background: #004080; transform: skewX(-7deg); padding: 4px 16px 3px 16px;">
                <section style="transform: skewX(7deg);">
                    <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px; word-break: break-word; font-family: Optima-Regular, PingFangTC-light;">
                        {section_title}
                    </section>
                </section>
            </section>
        </section>
        """
    
    elif method == 4:  # fit-content + margin auto
        bar_html = f"""
        <section style="width: fit-content; margin: 8px auto 0 auto; display: block;">
            <section style="background: #004080; transform: skewX(-7deg); padding: 4px 16px 3px 16px; text-align: center;">
                <section style="transform: skewX(7deg);">
                    <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px; word-break: break-word; font-family: Optima-Regular, PingFangTC-light;">
                        {section_title}
                    </section>
                </section>
            </section>
        </section>
        """
    
    elif method == 5:  # table + margin auto
        bar_html = f"""
        <section style="display: table; margin: 8px auto 0 auto;">
            <section style="background: #004080; transform: skewX(-7deg); padding: 4px 16px 3px 16px; text-align: center;">
                <section style="transform: skewX(7deg);">
                    <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px; word-break: break-word; font-family: Optima-Regular, PingFangTC-light;">
                        {section_title}
                    </section>
                </section>
            </section>
        </section>
        """
    
    elif method == 6:  # transform translate (需要relative父容器)
        bar_html = f"""
        <section style="position: relative; margin-top: 8px;">
            <section style="position: absolute; left: 50%; transform: translateX(-50%); background: #004080; transform: skewX(-7deg) translateX(-50%); padding: 4px 16px 3px 16px;">
                <section style="transform: skewX(7deg);">
                    <section style="font-weight: bold; font-size: 18px; color: rgb(255, 255, 255); line-height: 25px; word-break: break-word; font-family: Optima-Regular, PingFangTC-light;">
                        {section_title}
                    </section>
                </section>
            </section>
            <section style="height: 35px;"></section>
        </section>
        """
    
    return f"""
    <section style="width: 100%; margin: 32px 0;">
        {number_html}
        <p style="font-size: 14px; color: #999; margin: 5px 0; text-align: center;">{CENTERING_METHODS[method]}</p>
        {bar_html}
    </section>
    """

def convert_markdown_to_html(markdown_file: str, output_file: str):
    """转换Markdown到HTML，每个标题使用不同的居中方案"""
    # 读取Markdown
    md_path = Path(markdown_file)
    md_content = md_path.read_text(encoding='utf-8')
    
    # 转换到HTML
    md = markdown.Markdown(extensions=["extra", "sane_lists", "fenced_code"])
    html = md.convert(md_content)
    
    # 解析HTML
    soup = BeautifulSoup(html, 'lxml')
    
    # 移除h1
    for h1 in soup.find_all("h1"):
        h1.decompose()
    
    # 处理h2标题，每个使用不同的居中方案
    section_number = 0
    for h2 in soup.find_all("h2"):
        section_number += 1
        section_title = h2.get_text().strip()
        
        # 循环使用6种方案（1-6）
        method = ((section_number - 1) % 6) + 1
        
        # 生成新标题HTML
        new_title_html = get_title_html(section_number, section_title, method)
        new_section = BeautifulSoup(new_title_html, 'lxml')
        
        h2.replace_with(new_section)
    
    # 添加段落样式
    for p in soup.find_all("p"):
        if not p.get("style"):
            p["style"] = "font-size: 15px; margin: 14px 0; line-height: 1.6; color: rgb(51, 51, 51);"
    
    # 生成完整HTML
    full_html = f"""
<section style="padding: 0 8px; font-family: Optima-Regular, PingFangTC-light;">
    <div style="font-size: 15px; color: rgb(51, 51, 51);">
        {str(soup)}
    </div>
</section>
    """
    
    # 保存
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_html, encoding='utf-8')
    
    print(f"✅ 转换成功！")
    print(f"📄 HTML 已保存到: {output_file}")
    print(f"📊 共测试 {section_number} 种居中方案")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python test_title_centering.py <markdown文件> <输出HTML>")
        sys.exit(1)
    
    convert_markdown_to_html(sys.argv[1], sys.argv[2])
