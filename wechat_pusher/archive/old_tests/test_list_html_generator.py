#!/usr/bin/env python3
"""
生成不同格式的列表HTML，用于测试微信公众号编辑器的行为
"""
from pathlib import Path

def generate_test_html():
    """生成测试HTML文件"""

    html_content = """
<section style="padding: 0px 8px; font-family: Optima-Regular, PingFangTC-light;">
  <h2 style="display: table; margin: 32px auto; background: rgb(15, 76, 129); color: white; padding: 0px 0.2em; font-size: 16.8px; font-weight: bold;">
    列表格式测试
  </h2>

  <!-- 测试1：li内直接文本 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试1：li内直接文本
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第一项文本</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第二项文本</li>
  </ol>

  <!-- 测试2：li内使用p标签 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试2：li内使用p标签
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <p style="margin: 0; padding: 0;">第一项文本</p>
    </li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <p style="margin: 0; padding: 0;">第二项文本</p>
    </li>
  </ol>

  <!-- 测试3：li内使用span标签 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试3：li内使用span标签
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <span>第一项文本</span>
    </li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <span>第二项文本</span>
    </li>
  </ol>

  <!-- 测试4：无冒号 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试4：无冒号
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第一项文本</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第二项文本</li>
  </ol>

  <!-- 测试5：冒号后空格 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试5：冒号后空格
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">标题: 内容文本</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">标题: 内容文本</li>
  </ol>

  <!-- 测试6：冒号后无空格 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试6：冒号后无空格
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">标题:内容文本</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">标题:内容文本</li>
  </ol>

  <!-- 测试7：长文本直接文本 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试7：长文本直接文本
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第一项：这是一段很长的文字内容，用来测试在移动端设备上显示时的换行效果。当屏幕宽度有限时，这段文字会自动换行到下一行。</li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">第二项：另一段长文字内容，包含了一些技术术语和详细说明，用来测试换行效果和移动端显示。</li>
  </ol>

  <!-- 测试8：长文本使用span包裹 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试8：长文本使用span包裹
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-break: 0.5em;">
      <span>第一项：这是一段很长的文字内容，用来测试在移动端设备上显示时的换行效果。当屏幕宽度有限时，这段文字会自动换行到下一行。</span>
    </li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <span>第二项：另一段长文字内容，包含了一些技术术语和详细说明，用来测试换行效果和移动端显示。</span>
    </li>
  </ol>

  <!-- 测试9：使用section包裹li内容 -->
  <h3 style="border-left: 3px solid rgb(15, 76, 129); padding-left: 0.5em; margin-top: 1.5em; font-size: 16px; font-weight: bold;">
    测试9：使用section包裹li内容
  </h3>
  <ol style="margin: 10px 0; padding-left: 2em; color: rgb(51, 51, 51);">
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <section>第一项：这是一段很长的文字内容，用来测试在移动端设备上显示时的换行效果。当屏幕宽度有限时，这段文字会自动换行到下一行。</section>
    </li>
    <li style="line-height: 1.75; font-size: 14px; margin-bottom: 0.5em;">
      <section>第二项：另一段长文字内容，包含了一些技术术语和详细说明，用来测试换行效果和移动端显示。</section>
    </li>
  </ol>

</section>
"""

    # 保存HTML文件
    output_path = Path("output/test_list_formats.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")

    print(f"✅ 测试HTML已生成: {output_path}")
    print("\n📋 测试内容：")
    print("1. li内直接文本")
    print("2. li内使用p标签")
    print("3. li内使用span标签")
    print("4. 无冒号")
    print("5. 冒号后空格")
    print("6. 冒号后无空格")
    print("7. 长文本直接文本")
    print("8. 长文本使用span包裹")
    print("9. 使用section包裹li内容")
    print("\n💡 请手动上传此文件到微信公众号，查看哪种格式不会出现换行符")

if __name__ == "__main__":
    generate_test_html()
