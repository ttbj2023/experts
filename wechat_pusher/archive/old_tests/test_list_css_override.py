#!/usr/bin/env python3
"""
测试CSS属性覆盖微信编辑器默认列表样式
"""
from pathlib import Path

def generate_css_override_test():
    """生成CSS覆盖测试"""

    html_content = """
<section style="padding: 0px 8px;">
  <h2 style="display: table; margin: 32px auto; background: rgb(15, 76, 129); color: white; padding: 0px 0.2em; font-size: 16.8px; font-weight: bold;">
    CSS属性覆盖测试
  </h2>

  <!-- 测试1: list-style-position: inside -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试1: list-style-position: inside
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; list-style-position: inside;">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第一项：这是测试内容</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第二项：这是测试内容</li>
  </ol>

  <!-- 测试2: list-style-position: outside -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试2: list-style-position: outside
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; list-style-position: outside;">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第一项：这是测试内容</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第二项：这是测试内容</li>
  </ol>

  <!-- 测试3: text-indent: 0 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试3: text-indent: 0
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em;">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; text-indent: 0;">第一项：这是测试内容</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; text-indent: 0;">第二项：这是测试内容</li>
  </ol>

  <!-- 测试4: padding-left: 0 on li -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试4: li的padding-left: 0
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em;">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; padding-left: 0;">第一项：这是测试内容</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; padding-left: 0;">第二项：这是测试内容</li>
  </ol>

  <!-- 测试5: display: inline on li -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试5: li的display: inline
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em;">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; display: inline;">第一项：这是测试内容</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; display: inline;">第二项：这是测试内容</li>
  </ol>

  <!-- 测试6: 使用section包裹内容 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试6: 使用section包裹内容，display: inline-block
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em;">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <section style="display: inline-block;">第一项：这是测试内容</section>
    </li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <section style="display: inline-block;">第二项：这是测试内容</section>
    </li>
  </ol>

  <!-- 测试7: 微信官方建议 text-indent: 2em -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试7: 微信官方建议 text-indent: 2em
  </h3>
  <ol style="padding-left: 20px;">
    <li style="text-indent: 2em; line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第一项：这是测试内容</li>
    <li style="text-indent: 2em; line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第二项：这是测试内容</li>
  </ol>

  <!-- 测试8: 负的text-indent -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试8: text-indent: -1em (负缩进)
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em;">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; text-indent: -1em;">第一项：这是测试内容</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em; text-indent: -1em;">第二项：这是测试内容</li>
  </ol>

</section>
"""

    output_path = Path("output/test_css_override.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")

    print(f"✅ CSS覆盖测试已生成: {output_path}")
    print("\n📋 测试内容：")
    print("1. list-style-position: inside")
    print("2. list-style-position: outside")
    print("3. text-indent: 0")
    print("4. li的padding-left: 0")
    print("5. li的display: inline")
    print("6. 使用section包裹 + display: inline-block")
    print("7. 微信官方建议: text-indent: 2em")
    print("8. text-indent: -1em (负缩进)")

if __name__ == "__main__":
    generate_css_override_test()
