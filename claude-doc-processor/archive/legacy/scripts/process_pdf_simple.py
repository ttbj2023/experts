#!/usr/bin/env python3
"""
使用 GLM-4.6V-Flash 逐页处理 PDF 文档（优化版）
改进：
1. 压缩图片减少base64大小
2. 增加max_tokens避免截断
3. 优化提示词避免输出思考过程
4. 添加重试机制
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


class GLM46VProcessor:
    """GLM-4.6V-Flash PDF 处理器（优化版）"""

    def __init__(self, api_url: str = "http://192.168.100.110:9999"):
        self.api_url = api_url.rstrip('/')
        self.model_name = "glm-4.6v-flash"
        self.max_retries = 3  # 重试次数

    def compress_image(self, image_path: str, max_size: int = 768, quality: int = 75) -> str:
        """
        压缩图片以减少base64大小
        优化：降低默认尺寸和质量以控制token消耗

        Args:
            image_path: 原始图片路径
            max_size: 最大边长（像素）- 默认768以控制tokens
            quality: JPEG质量（1-100）- 默认75以平衡大小和质量

        Returns:
            压缩后的base64字符串
        """
        img = Image.open(image_path)

        # 计算缩放比例
        width, height = img.size
        if max(width, height) > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 转换为RGB（如果需要）
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 压缩为JPEG
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)

        # 编码为base64
        compressed = base64.b64encode(buffer.read()).decode('utf-8')

        # 调试信息
        original_size = os.path.getsize(image_path)
        compressed_size = len(compressed) * 3 // 4  # base64解码后大小
        print(f"    📐 图片压缩: {original_size//1024}KB → {compressed_size//1024}KB (max_size={max_size}, quality={quality})")

        return compressed

    def pdf_to_images(self, pdf_path: str, output_dir: str, max_pages: Optional[int] = None, dpi: int = 150) -> list:
        """
        将 PDF 转换为图片

        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            max_pages: 最大处理页数（None 表示全部）
            dpi: 分辨率（降低以减少文件大小）

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

            # 使用较低的DPI以减少图片大小
            mat = fitz.Matrix(dpi / 72, dpi / 72)

            pix = page.get_pixmap(matrix=mat)

            image_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
            pix.save(image_path)
            image_paths.append(image_path)

            # 显示文件大小
            file_size = os.path.getsize(image_path) / 1024  # KB
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
        """
        调用 GLM-4.6V-Flash API（带重试）

        Args:
            image_base64: base64 编码的图片
            prompt: 提示词
            max_tokens: 最大tokens
            retry_count: 当前重试次数

        Returns:
            API 响应
        """
        headers = {
            "Content-Type": "application/json"
        }

        # 构造请求体
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
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
                timeout=180  # 3分钟超时
            )

            if response.status_code == 400:
                # 如果是400错误，尝试进一步压缩图片
                if retry_count < self.max_retries:
                    print(f"  ⚠️  400错误，尝试重新压缩图片并重试 ({retry_count + 1}/{self.max_retries})...")
                    time.sleep(2)
                    return {"retry": True}  # 标记需要重试
                else:
                    print(f"  ❌ 重试{self.max_retries}次后仍失败")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                print(f"  ⚠️  API调用失败: {e}，重试中 ({retry_count + 1}/{self.max_retries})...")
                time.sleep(3)
                return {"retry": True, "error": str(e)}
            else:
                print(f"  ❌ 重试{self.max_retries}次后仍失败: {e}")
                return {"error": str(e)}

    def process_page(self, image_path: str, page_num: int, max_tokens: int = 65536) -> Optional[str]:
        """
        处理单个页面

        Args:
            image_path: 图片路径
            page_num: 页码
            max_tokens: 最大tokens (默认64K，可根据需求调整)

        Returns:
            Markdown 格式的文本
        """
        print(f"\n🔄 处理第 {page_num} 页...")

        # 直接输出的提示词（增强版）
        prompt = """请将这个PDF页面转换为Markdown格式。直接输出内容，不要添加任何解释或思考过程。

格式要求：
1. **标题层级**：使用 # ## ### #### 表示不同级别标题
2. **表格格式**：
   - 必须使用标准Markdown表格语法
   - 表头行和数据行之间必须有分隔行（如 |---|---|）
   - 确保所有列对齐正确
   - 表格中不能有空列
3. **数学公式**：
   - 行内公式使用 $...$ 格式
   - 独立公式行使用 $$...$$ 格式
   - 使用标准LaTeX语法（如 \frac{a}{b}、\sqrt{x}、\sum_{i=1}^{n}）
   - 保持原公式的准确性
4. **其他格式**：
   - 列表使用 - 或 1. 格式
   - 保留原文的缩进和层级关系
   - 代码块用 ```语言 包裹

特别注意：
- 不要输出任何思考过程或解释性文字
- 确保表格格式完全正确（表头、分隔行、数据行完整）
- 数学公式必须使用LaTeX格式，不要用纯文本
- 保留所有关键信息，不要遗漏
"""

        # 压缩图片（使用中等尺寸以平衡识别精度和token消耗）
        image_base64 = self.compress_image(image_path, max_size=768, quality=75)

        # 调用 API（带重试）
        for retry in range(self.max_retries + 1):
            start_time = time.time()
            response = self.call_glm46v_api(image_base64, prompt, max_tokens, retry_count=retry)
            elapsed_time = time.time() - start_time

            # 检查是否需要重试
            if response.get("retry"):
                # 进一步压缩图片
                if retry == 0:
                    image_base64 = self.compress_image(image_path, max_size=1024, quality=70)
                elif retry == 1:
                    image_base64 = self.compress_image(image_path, max_size=768, quality=60)
                continue

            # 提取结果
            if "error" in response:
                print(f"❌ 第 {page_num} 页处理失败: {response['error']}")
                return None

            try:
                content = response["choices"][0]["message"]["content"]
                tokens_used = response.get("usage", {}).get("total_tokens", "N/A")

                # 过滤掉  标记之间的思考内容
                import re
                # 使用正则表达式删除 <think>...</think> 及其内容
                # 1. 删除 <|beginofthink|> 和 <|endofthink|> 标签（保留内容）
                content = re.sub(r'<\|beginofthink\|>', '', content)
                content = re.sub(r'<\|endofthink\|>', '', content)

                # 2. 删除 <|beginofbox|> 和 <|endofbox|> 标签（保留内容）
                content = re.sub(r'<\|beginofbox\|>', '', content)
                content = re.sub(r'<\|endofbox\|>', '', content)

                # 清理可能的多余空白
                content = content.strip()

                print(f"  ✓ 第 {page_num} 页处理完成 (耗时: {elapsed_time:.1f}s, tokens: {tokens_used})")

                return content

            except (KeyError, IndexError) as e:
                print(f"❌ 解析响应失败: {e}")
                print(f"   响应内容: {json.dumps(response, ensure_ascii=False)[:500]}")
                return None

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

        # 转换 PDF 为图片（提高DPI以获得更好的识别效果）
        print(f"\n📖 开始处理 PDF: {pdf_name}")
        image_paths = self.pdf_to_images(pdf_path, images_dir, max_pages, dpi=200)

        # 逐页处理
        markdown_content = f"# {pdf_name}\n\n"
        markdown_content += f"**处理时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**处理模型**: {self.model_name}\n"
        markdown_content += f"**总页数**: {len(image_paths)}\n\n"
        markdown_content += "---\n\n"

        success_count = 0
        for idx, image_path in enumerate(image_paths, start=start_page):
            page_content = self.process_page(image_path, idx)  # 使用默认的131072 (128K)

            if page_content:
                markdown_content += f"\n## 第 {idx} 页\n\n"
                markdown_content += page_content
                markdown_content += "\n\n---\n\n"

                # 保存单页结果
                single_page_md = os.path.join(markdown_dir, f"page_{idx:03d}.md")
                with open(single_page_md, "w", encoding="utf-8") as f:
                    f.write(f"# 第 {idx} 页\n\n{page_content}")

                success_count += 1

        # 保存完整结果
        output_md = os.path.join(markdown_dir, f"{pdf_name}_full.md")
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"\n✅ 处理完成！")
        print(f"   📊 成功: {success_count}/{len(image_paths)} 页")
        print(f"   📁 输出目录: {markdown_dir}")
        print(f"   📄 Markdown 文件: {output_md}")

        return output_md


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="使用 GLM-4.6V-Flash 处理 PDF 文档（优化版）")
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("-o", "--output", default="./output_glm46v_v2", help="输出目录（默认: ./output_glm46v_v2）")
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
