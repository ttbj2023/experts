#!/usr/bin/env python3
"""
使用 GLM-4.6V-Flash 逐页处理 PDF 文档
调用本地 LM Studio API 进行高精度文档识别
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


class GLM46VProcessor:
    """GLM-4.6V-Flash PDF 处理器"""

    def __init__(self, api_url: str = "http://192.168.100.110:9999"):
        self.api_url = api_url.rstrip('/')
        self.model_name = "glm-4.6v-flash"

    def pdf_to_images(self, pdf_path: str, output_dir: str, max_pages: Optional[int] = None) -> list:
        """
        将 PDF 转换为图片

        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            max_pages: 最大处理页数（None 表示全部）

        Returns:
            图片文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)

        pdf_document = fitz.open(pdf_path)
        image_paths = []

        total_pages = len(pdf_document)
        process_pages = min(total_pages, max_pages) if max_pages else total_pages

        print(f"📄 PDF 总页数: {total_pages}, 将处理: {process_pages} 页")

        for page_num in range(process_pages):
            page = pdf_document[page_num]

            # 设置缩放比例以获得高质量图片
            zoom = 2.0  # 放大倍数
            mat = fitz.Matrix(zoom, zoom)

            pix = page.get_pixmap(matrix=mat)

            image_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
            pix.save(image_path)
            image_paths.append(image_path)

            print(f"  ✓ 第 {page_num + 1}/{process_pages} 页已转换")

        pdf_document.close()
        return image_paths

    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def call_glm46v_api(self, image_base64: str, prompt: str = "请识别这个PDF页面的内容，包括文字、公式、表格等。请以Markdown格式输出，保持原有的排版结构和层次。") -> Dict[str, Any]:
        """
        调用 GLM-4.6V-Flash API

        Args:
            image_base64: base64 编码的图片
            prompt: 提示词

        Returns:
            API 响应
        """
        headers = {
            "Content-Type": "application/json"
        }

        # 构造请求体（兼容 LM Studio 的 OpenAI API 格式）
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.1,  # 降低随机性，提高稳定性
            "max_tokens": 4096
        }

        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120  # 2分钟超时
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ API 调用失败: {e}")
            return {"error": str(e)}

    def process_page(self, image_path: str, page_num: int) -> Optional[str]:
        """
        处理单个页面

        Args:
            image_path: 图片路径
            page_num: 页码

        Returns:
            Markdown 格式的文本
        """
        print(f"\n🔄 处理第 {page_num} 页...")

        # 编码图片
        image_base64 = self.encode_image_to_base64(image_path)

        # 调用 API
        start_time = time.time()
        response = self.call_glm46v_api(image_base64)
        elapsed_time = time.time() - start_time

        # 提取结果
        if "error" in response:
            print(f"❌ 第 {page_num} 页处理失败: {response['error']}")
            return None

        try:
            # 尝试从 OpenAI 格式响应中提取内容
            content = response["choices"][0]["message"]["content"]
            tokens_used = response.get("usage", {}).get("total_tokens", "N/A")

            print(f"  ✓ 第 {page_num} 页处理完成 (耗时: {elapsed_time:.1f}s, tokens: {tokens_used})")
            return content

        except (KeyError, IndexError) as e:
            print(f"❌ 解析响应失败: {e}")
            print(f"   响应内容: {json.dumps(response, ensure_ascii=False)[:500]}")
            return None

    def process_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        max_pages: Optional[int] = None,
        start_page: int = 1
    ) -> str:
        """
        处理 PDF 文档

        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            max_pages: 最大处理页数
            start_page: 起始页码

        Returns:
            输出的 Markdown 文件路径
        """
        pdf_name = Path(pdf_path).stem
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 创建子目录
        images_dir = os.path.join(output_dir, f"{pdf_name}_{timestamp}", "images")
        markdown_dir = os.path.join(output_dir, f"{pdf_name}_{timestamp}")

        os.makedirs(markdown_dir, exist_ok=True)

        # 转换 PDF 为图片
        print(f"\n📖 开始处理 PDF: {pdf_name}")
        image_paths = self.pdf_to_images(pdf_path, images_dir, max_pages)

        # 逐页处理
        markdown_content = f"# {pdf_name}\n\n"
        markdown_content += f"**处理时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**处理模型**: {self.model_name}\n\n"
        markdown_content += "---\n\n"

        for idx, image_path in enumerate(image_paths, start=start_page):
            page_content = self.process_page(image_path, idx)

            if page_content:
                markdown_content += f"\n## 第 {idx} 页\n\n"
                markdown_content += page_content
                markdown_content += "\n\n---\n\n"

                # 保存单页结果
                single_page_md = os.path.join(markdown_dir, f"page_{idx:03d}.md")
                with open(single_page_md, "w", encoding="utf-8") as f:
                    f.write(f"# 第 {idx} 页\n\n{page_content}")

        # 保存完整结果
        output_md = os.path.join(markdown_dir, f"{pdf_name}_full.md")
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"\n✅ 处理完成！")
        print(f"   📁 输出目录: {markdown_dir}")
        print(f"   📄 Markdown 文件: {output_md}")

        return output_md


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="使用 GLM-4.6V-Flash 处理 PDF 文档")
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("-o", "--output", default="./output_glm46v", help="输出目录（默认: ./output_glm46v）")
    parser.add_argument("-n", "--max-pages", type=int, default=None, help="最大处理页数")
    parser.add_argument("-s", "--start-page", type=int, default=1, help="起始页码（默认: 1）")
    parser.add_argument("--api-url", default="http://192.168.100.110:9999", help="LM Studio API 地址")

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.pdf_path):
        print(f"❌ 错误: PDF 文件不存在: {args.pdf_path}")
        sys.exit(1)

    # 创建处理器
    processor = GLM46VProcessor(api_url=args.api_url)

    # 处理 PDF
    output_md = processor.process_pdf(
        args.pdf_path,
        args.output,
        max_pages=args.max_pages,
        start_page=args.start_page
    )

    print(f"\n🎉 全部完成！输出文件: {output_md}")


if __name__ == "__main__":
    main()
