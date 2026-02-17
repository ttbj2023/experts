#!/usr/bin/env python3
"""
使用 GLM-4.6V-Flash 直接将 PDF 转换为 HTML
改进：跳过Markdown中间步骤，直接生成HTML

优势：
1. 减少转换步骤，提高效率
2. HTML标签更准确
3. 减少格式丢失

劣势：
1. 需要额外的CSS样式文件
2. HTML结构可能不够统一
"""

import os
import sys
import base64
import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image


class GLM46VToHTMLProcessor:
    """GLM-4.6V-Flash PDF转HTML处理器（直接输出HTML）"""

    def __init__(self, api_url: str = "http://192.168.100.110:9999"):
        self.api_url = api_url.rstrip('/')
        self.model_name = "zai-org/glm-4.6v-flash"
        self.max_retries = 3

    def compress_image(self, image_path: str, max_size: int = 1280, quality: int = 85) -> str:
        """压缩图片"""
        img = Image.open(image_path)
        width, height = img.size

        if max(width, height) > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        buffer.seek(0)

        compressed = base64.b64encode(buffer.read()).decode('utf-8')
        return compressed

    def pdf_to_images(self, pdf_path: str, output_dir: str, max_pages: Optional[int] = None, dpi: int = 200) -> list:
        """将PDF转换为图片"""
        os.makedirs(output_dir, exist_ok=True)
        pdf_document = fitz.open(pdf_path)
        image_paths = []

        total_pages = len(pdf_document)
        process_pages = min(total_pages, max_pages) if max_pages else total_pages

        print(f"📄 PDF总页数: {total_pages}, 将处理: {process_pages} 页")

        for page_num in range(process_pages):
            page = pdf_document[page_num]
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            image_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
            pix.save(image_path)
            image_paths.append(image_path)
            file_size = os.path.getsize(image_path) / 1024
            print(f"  ✓ 第 {page_num + 1}/{process_pages} 页已转换 ({file_size:.1f} KB)")

        pdf_document.close()
        return image_paths

    def call_glm46v_api(
        self,
        image_base64: str,
        prompt: str,
        max_tokens: int = 8192,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """调用GLM-4.6V-Flash API"""
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=180
            )

            if response.status_code == 400:
                if retry_count < self.max_retries:
                    return {"retry": True}
                else:
                    return {"error": "Max retries exceeded"}

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                return {"retry": True, "error": str(e)}
            else:
                return {"error": str(e)}

    def process_page(self, image_path: str, page_num: int, max_tokens: int = 8192) -> Optional[str]:
        """处理单个页面，直接输出HTML"""
        print(f"\n🔄 处理第 {page_num} 页...")

        # 直接输出HTML的prompt
        prompt = r"""请将这个PDF页面转换为HTML格式。这是数学教辅材料，请严格按照以下要求处理：

## 一、页眉页脚处理（重要）
- 完全忽略页面顶部的页眉（书名、章节名、重复的标题等）
- 完全忽略页面底部的页脚（页码、版权信息、网址等）
- 只保留正文主要内容

## 二、双栏布局处理
本教材采用"主内容 + 注释"的双栏设计：
- 主栏（较宽）：例题、讲解、练习题等主要教学内容
- 副栏（较窄）：注释、提示、要点说明、解题思路等辅助内容

处理方式：
1. 主内容使用标准HTML标签（<p>, <div>, <section>等）
2. 注释内容使用<blockquote class="side-note">标签
3. 将注释嵌入到主内容的对应位置

## 三、数学公式处理
- 行内公式：使用LaTeX格式，包裹在<span class="math-inline">\( ... \)</span>中
  例如：<span class="math-inline">\(x^2 + 2x + 1 = 0\)</span>
- 独立公式：使用<div class="math-display">$$ ... $$</div>
  例如：<div class="math-display">$$\frac{a}{b} = \frac{c}{d}$$</div>
- 使用标准LaTeX语法：
  - 分数：\frac{分子}{分母}
  - 根号：\sqrt{表达式}
  - 求和：\sum_{i=1}^{n}
  - 积分：\int_{a}^{b}
  - 极限：\lim_{x \to \infty}
  - 上标下标：x^2、a_n

## 四、表格处理
- 使用标准HTML表格结构：<table>, <tr>, <th>, <td>
- 为表格添加class="outer-border"
- 第一行使用<th>表示表头
- 表头添加背景色：style="background: #4472C4; color: #fff;"
- 示例：
```html
<table class="outer-border">
  <tr>
    <th style="background: #4472C4; color: #fff;">列1</th>
    <th style="background: #4472C4; color: #fff;">列2</th>
  </tr>
  <tr>
    <td>数据1</td>
    <td>数据2</td>
  </tr>
</table>
```

## 五、标题层级
- 使用<h1>, <h2>, <h3>, <h4>表示不同级别标题
- 保持原始标题层级关系
- 示例：<h2>24.1 数据的集中趋势</h2>

## 六、段落和列表
- 段落使用<p>标签
- 无序列表使用<ul><li>
- 有序列表使用<ol><li>
- 列表项可以嵌套

## 七、禁止事项
- 禁止输出任何思考过程或解释性文字
- 禁止使用Markdown语法（这是HTML输出，不是Markdown）
- 禁止使用```html代码块标记
- 禁止遗漏任何关键信息
- 禁止自行添加或删除内容
- 禁止使用绝对定位（position: absolute）
- 禁止添加style属性（除非表格表头背景色）

## 八、输出要求
直接输出HTML内容，从第一个标签开始，到最后一个标签结束。
不要添加任何说明、总结或前缀。
确保HTML结构完整、标签闭合正确。
"""

        # 压缩图片
        image_base64 = self.compress_image(image_path)

        # 调用API（带重试）
        for retry in range(self.max_retries + 1):
            start_time = time.time()
            response = self.call_glm46v_api(image_base64, prompt, max_tokens, retry_count=retry)
            elapsed_time = time.time() - start_time

            if response.get("retry"):
                if retry == 0:
                    image_base64 = self.compress_image(image_path, max_size=1024, quality=70)
                elif retry == 1:
                    image_base64 = self.compress_image(image_path, max_size=768, quality=60)
                continue

            if "error" in response:
                print(f"❌ 第 {page_num} 页处理失败: {response['error']}")
                return None

            try:
                content = response["choices"][0]["message"]["content"]
                tokens_used = response.get("usage", {}).get("total_tokens", "N/A")

                # 过滤思考内容
                import re
                content = re.sub(r'<\|begin_of_thinking\|>.*?<\|end_of_thinking\|>', '', content, flags=re.DOTALL)
                content = re.sub(r'<\|beginofbox\|>', '', content)
                content = re.sub(r'<\|endofbox\|>', '', content)
                content = content.strip()

                # 清理可能的```html标记
                content = re.sub(r'^```html\n?', '', content)
                content = re.sub(r'\n?```$', '', content)

                print(f"  ✓ 第 {page_num} 页处理完成 (耗时: {elapsed_time:.1f}s, tokens: {tokens_used})")

                return content

            except (KeyError, IndexError) as e:
                print(f"❌ 解析响应失败: {e}")
                return None

        return None

    def process_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        max_pages: Optional[int] = None,
        start_page: int = 1
    ) -> str:
        """处理PDF文档"""
        pdf_name = Path(pdf_path).stem
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        images_dir = os.path.join(output_dir, f"{pdf_name}_{timestamp}", "images")
        html_dir = os.path.join(output_dir, f"{pdf_name}_{timestamp}")

        os.makedirs(html_dir, exist_ok=True)

        # 转换PDF为图片
        print(f"\n📖 开始处理PDF: {pdf_name}")
        image_paths = self.pdf_to_images(pdf_path, images_dir, max_pages, dpi=200)

        # 逐页处理
        html_parts = []
        success_count = 0

        for idx, image_path in enumerate(image_paths, start=start_page):
            page_html = self.process_page(image_path, idx)

            if page_html:
                html_parts.append(page_html)
                success_count += 1

        # 合并所有页面
        all_html = '\n\n'.join(html_parts)

        # 添加完整的HTML框架和CSS
        full_html = self._wrap_html(all_html, pdf_name)

        # 保存完整HTML
        output_html = os.path.join(html_dir, f"{pdf_name}_full.html")
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(full_html)

        print(f"\n✅ 处理完成！")
        print(f"   📊 成功: {success_count}/{len(image_paths)} 页")
        print(f"   📁 输出目录: {html_dir}")
        print(f"   📄 HTML文件: {output_html}")

        return output_html

    def _wrap_html(self, body_content: str, title: str) -> str:
        """包装完整HTML文档"""
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <!-- MathJax for 数学公式渲染 -->
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    <style>
        /* ========== 全局样式 ========== */
        body {{
            font-family: "Times New Roman", "宋体", SimSun, serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #000;
            background: #fff;
            margin: 0;
            padding: 2cm;
        }}

        /* ========== 标题样式 ========== */
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            color: #000;
            margin: 18pt 0 12pt 0;
            border-bottom: 2px solid #000;
            padding-bottom: 6pt;
        }}

        h2 {{
            font-size: 16pt;
            font-weight: bold;
            color: #000;
            margin: 16pt 0 10pt 0;
        }}

        h3 {{
            font-size: 14pt;
            font-weight: bold;
            color: #000;
            margin: 14pt 0 8pt 0;
        }}

        h4 {{
            font-size: 12pt;
            font-weight: bold;
            color: #000;
            margin: 12pt 0 6pt 0;
        }}

        /* ========== 段落样式 ========== */
        p {{
            margin: 6pt 0;
            text-align: justify;
        }}

        /* ========== 数学公式 ========== */
        .math-inline {{
            font-family: "Cambria Math", "Times New Roman", serif;
            font-style: italic;
        }}

        .math-display {{
            font-family: "Cambria Math", "Times New Roman", serif;
            display: block;
            text-align: center;
            margin: 12pt 0;
            padding: 8pt;
            background: #f9f9f9;
            border-left: 3px solid #4472C4;
        }}

        /* ========== 表格样式 ========== */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
        }}

        table.outer-border {{
            border: 2pt solid #000;
        }}

        th, td {{
            border: 1pt solid #000;
            padding: 6pt 8pt;
            text-align: center;
            vertical-align: middle;
        }}

        tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        /* ========== 引用块样式（注释） ========== */
        blockquote {{
            margin: 12pt 0;
            padding: 8pt 12pt;
            background: #f5f5f5;
            border-left: 4px solid #4472C4;
            font-style: italic;
            color: #666;
        }}

        blockquote p {{
            margin: 0;
        }}

        /* ========== 列表样式 ========== */
        ul, ol {{
            margin: 6pt 0;
            padding-left: 2em;
        }}

        li {{
            margin: 3pt 0;
        }}

        /* ========== 分隔线 ========== */
        hr {{
            border: none;
            border-top: 1pt solid #000;
            margin: 18pt 0;
        }}

        /* ========== 打印优化 ========== */
        @media print {{
            body {{
                background: white;
            }}

            h1, h2, h3, h4, table, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
{body_content}
</body>
</html>'''
        return html


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="使用 GLM-4.6V-Flash 直接将PDF转换为HTML")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", default="./output_glm46v_html", help="输出目录（默认: ./output_glm46v_html）")
    parser.add_argument("-n", "--max-pages", type=int, default=None, help="最大处理页数")
    parser.add_argument("-s", "--start-page", type=int, default=1, help="起始页码（默认: 1）")
    parser.add_argument("--api-url", default="http://192.168.100.110:9999", help="LM Studio API地址")

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"❌ 错误: PDF文件不存在: {args.pdf_path}")
        sys.exit(1)

    processor = GLM46VToHTMLProcessor(api_url=args.api_url)

    output_html = processor.process_pdf(
        args.pdf_path,
        args.output,
        max_pages=args.max_pages,
        start_page=args.start_page
    )

    print(f"\n🎉 全部完成！输出文件: {output_html}")


if __name__ == "__main__":
    main()
