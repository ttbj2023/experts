#!/usr/bin/env python3
"""
使用 GLM-4.6V-Flash 逐页处理 PDF 文档（通用版）
适用范围：学术论文、图书、杂志、技术文档、教辅书等各种类型文档

改进：
1. 压缩图片减少base64大小
2. 增加max_tokens避免截断
3. 优化提示词避免输出思考过程
4. 添加重试机制
5. **通用布局识别**：自动识别并处理各种文档布局
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
    """GLM-4.6V-Flash PDF 处理器（通用版）"""

    def __init__(self, api_url: str = "http://192.168.100.110:9999"):
        self.api_url = api_url.rstrip('/')
        self.model_name = "zai-org/glm-4.6v-flash"  # 使用完整的模型ID
        self.max_retries = 3  # 重试次数

    def compress_image(self, image_path: str, max_size: int = 1024, quality: int = 70,
                   compression: str = "medium") -> str:
        """
        压缩图片以减少base64大小
        优化：降低默认尺寸和质量以控制token消耗

        Args:
            image_path: 原始图片路径
            max_size: 最大边长（像素）
            quality: JPEG质量（1-100）
            compression: 压缩级别 - none/low/medium/high/ultra (默认: medium)

        Returns:
            压缩后的base64字符串
        """
        img = Image.open(image_path)

        # 计算缩放比例
        width, height = img.size

        # 根据压缩级别调整参数
        size_params = {
            "none": (99999, 100),    # 原始尺寸
            "low": (1920, 90),        # 低压缩（1920px高清配置）
            "medium": (1280, 85),     # 中等压缩（1280px平衡配置）
            "high": (1024, 80),       # 高压缩（1024px标准配置）
            "ultra": (768, 75)        # 超高压缩（768px快速配置）
        }
        max_size_actual, quality_actual = size_params.get(compression, (max_size, quality))

        if max(width, height) > max_size_actual:
            if width > height:
                new_width = max_size_actual
                new_height = int(height * (max_size_actual / width))
            else:
                new_height = max_size_actual
                new_width = int(width * (max_size_actual / height))

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
        print(f"    📐 图片压缩: {original_size//1024}KB → {compressed_size//1024}KB (max_size={max_size_actual}, quality={quality_actual}, compression={compression})")

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
        max_tokens: int = 65536,
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

        # 通用文档提示词（Universal版本 - 智能布局识别，精简版）
        prompt = r"""请将这个PDF页面转换为Markdown格式。请严格按照以下要求处理：

【最严禁令】无论任何情况，绝对禁止使用代码块语法（``` 或 ~~~）！所有内容必须是直接的Markdown格式！

## 一、页眉页脚处理
- 完全忽略页面顶部的页眉（书名、章节名、重复的标题、公司logo等）
- 完全忽略页面底部的页脚（页码、版权信息、网址、日期等）
- 只保留正文主要内容

## 二、布局处理

按页面实际布局提取内容：

**单栏文档**（图书、报告）：从上到下提取，保持原有结构

**等宽双栏**（学术论文、期刊）：
- 优先按栏组织，使用"## 左栏内容"和"## 右栏内容"区分
- 或按自然阅读顺序（从上到下、从左到右）逐段提取

**不等宽双栏**（教辅书、技术文档）：
- 主栏（宽）：正文、例题、主要内容
- 副栏（窄）：注释、提示、说明（用引用块>标记，嵌入主内容对应位置）

**图文混排**（杂志）：用图片占位符标记图片位置（格式见第五部分）

## 三、编号结构保护
完整保留所有编号结构：【例1】、练习1、2.1、Chapter 1、步骤1、（1）、(1)等

## 四、公式LaTeX化
- 行内公式：$x^2 + 2x + 1 = 0$
- 独立公式：$$\frac{a}{b} = \frac{c}{d}$$
- 使用标准LaTeX语法：\frac、\sqrt、\sum、\int、\lim、\alpha、\beta等

## 五、图片占位符（重要！）

页面中有图片时必须标记：
```html
<!-- IMAGE_PLACEHOLDER
type: <类型：示意图/函数图像/统计图表/技术图纸/科学插图等>
description: <详细描述，包括所有可见的文本、标注、数据、颜色等>
-->
```

## 六、Markdown格式规范
1. 标题：使用 # ## ### #### 表示层级
2. 表格：
   ```
   | 列1 | 列2 | 列3 |
   |-----|-----|-----|
   | 数据1 | 数据2 | 数据3 |
   ```
3. 列表：使用 - 或 1. 或 (1)
4. 强调：使用 **粗体** 或 *斜体*

## 七、特殊符号
直接使用Unicode字符：α β γ θ ∈ ∪ ∩ ⊆ ≠ ≤ ≥ ∞ → ← ° Ω μ

直接输出Markdown内容，不要添加任何说明或总结。
"""

        # 压缩图片（使用1280px平衡配置）
        # 可通过修改compression参数调整: none/raw/low/medium/high/ultra
        image_base64 = self.compress_image(image_path, compression="low")

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

                # 过滤掉  标签之间的思考内容
                import re
                # 使用正则表达式删除  标签及其内容
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

                # 2. 删除 <|beginofbox|> 和 <|endofbox|> 标签（保留内容）
                content = re.sub(r'<\|begin_of_box\|>', '', content)
                content = re.sub(r'<\|end_of_box\|>', '', content)
                content = re.sub(r'<\|beginofbox\|>', '', content)
                content = re.sub(r'<\|endofbox\|>', '', content)
                content = re.sub(r'<\|endofbox\|>$', '', content)  # 文档末尾的版本

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
        markdown_content = ""
        # 不添加元信息标题，直接从页面内容开始

        success_count = 0
        for idx, image_path in enumerate(image_paths, start=start_page):
            page_content = self.process_page(image_path, idx)  # 使用默认的65536(64K)

            if page_content:
                # 不添加页码标记，直接添加页面内容
                markdown_content += page_content
                markdown_content += "\n\n---\n\n"

                # 保存单页结果
                single_page_md = os.path.join(markdown_dir, f"page_{idx:03d}.md")
                with open(single_page_md, "w", encoding="utf-8") as f:
                    f.write(f"# 第 {idx} 页\n\n{page_content}")

                success_count += 1

        # 保存完整结果
        output_md = os.path.join(markdown_dir, f"{pdf_name}_full.md")
        try:
            with open(output_md, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                f.flush()
                os.fsync(f.fileno())

            # 验证文件已创建
            if not os.path.exists(output_md):
                raise Exception(f"文件未创建: {output_md}")

            file_size = os.path.getsize(output_md)
            print(f"\n✅ 处理完成！")
            print(f"   📊 成功: {success_count}/{len(image_paths)} 页")
            print(f"   📁 输出目录: {markdown_dir}")
            print(f"   📄 Markdown 文件: {output_md} ({file_size} bytes)")

            return output_md

        except Exception as e:
            print(f"   ❌ 保存Markdown文件失败: {str(e)}")
            # 即使full文件失败，也返回目录路径，让调用者可以读取page文件
            return markdown_dir


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="使用 GLM-4.6V-Flash 处理 PDF 文档（通用版 - 智能布局识别）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 处理整个PDF
  python3 %(prog)s document.pdf

  # 处理前10页（测试效果）
  python3 %(prog)s document.pdf -n 10

  # 从第5页开始处理
  python3 %(prog)s document.pdf -s 5

  # 指定输出目录
  python3 %(prog)s document.pdf -o ./my_output

  # 使用自定义API地址
  python3 %(prog)s document.pdf --api-url http://localhost:9999

适用文档类型：
  • 学术论文（IEEE/ACM双栏格式）
  • 技术图书（单栏或主副栏）
  • 杂志期刊（图文混排）
  • 教辅书（注释式双栏）
  • 技术文档（手册、说明书）
  • 报告白皮书（标准文档）
        """
    )
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("-o", "--output", default="./output_glm46v_universal", help="输出目录（默认: ./output_glm46v_universal）")
    parser.add_argument("-n", "--max-pages", type=int, default=None, help="最大处理页数（用于测试）")
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
