#!/usr/bin/env python3
"""
使用 Qwen3-VL-8B (Ollama) 逐页处理 PDF 文档
基于GLM-4.6V版本改造，适配Ollama API
改进：
1. 使用本地Ollama部署，无网络延迟
2. 测试Qwen3-VL-8B在数学教辅识别上的表现
3. 完整保留v3提示词（页眉页脚、双栏布局、表格分隔行）
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


class Qwen3VLProcessor:
    """Qwen3-VL-8B PDF 处理器 (Ollama部署）"""

    def __init__(self, api_url: str = "http://localhost:11434"):
        self.api_url = api_url.rstrip('/')
        self.model_name = "qwen3-vl:8b"
        self.max_retries = 3  # 重试次数

    def compress_image(self, image_path: str, max_size: int = 1024, quality: int = 70,
                   compression: str = "medium") -> str:
        """
        压缩图片以减少base64大小
        优化：降低默认尺寸和质量以控制token消耗

        Args:
            image_path: 原始图片路径
            max_size: 最大边长（像素）- 默认768以控制tokens
            quality: JPEG质量（1-100）- 默认75以平衡大小和质量
            compression: 压缩级别 - none/low/medium/high (默认: medium)

        Returns:
            压缩后的base64字符串
        """
        img = Image.open(image_path)

        # 计算缩放比例
        width, height = img.size

        # 根据压缩级别调整参数
        size_params = {
            "none": (99999, 100),    # 原始尺寸
            "low": (1280, 85),        # 低压缩（1280px平衡配置）
            "medium": (1024, 80),     # 中等压缩（1024px标准配置）
            "high": (768, 75),       # 高压缩（768px快速配置）
            "ultra": (512, 65)        # 超高压缩（512px极限配置）
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

    def call_qwen3vl_api(
        self,
        image_base64: str,
        prompt: str,
        max_tokens: int = 65536,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        调用 Ollama Qwen3-VL-8B API（带重试）

        Args:
            image_base64: base64 编码的图片
            prompt: 提示词
            max_tokens: 最大tokens (默认64K，与GLM-4.6V对比)
            retry_count: 当前重试次数

        Returns:
            API 响应（转换为统一格式）
        """
        # Ollama API格式（64K上下文配置）
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "options": {
                "num_ctx": 65536,  # 64K上下文
                "num_predict": max_tokens,
                "temperature": 0.1,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
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
            result = response.json()

            # 转换Ollama响应格式为统一格式（兼容后续代码）
            return {
                "choices": [{
                    "message": {
                        "content": result.get("response", "")
                    }
                }],
                "usage": {
                    "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                }
            }

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
            max_tokens: 最大tokens (默认64K，与GLM-4.6V一致)

        Returns:
            Markdown 格式的文本
        """
        print(f"\n🔄 处理第 {page_num} 页...")

        # 数学教辅专用提示词（v3版本 - 支持注释性双栏和页眉页脚过滤）
        # 使用64K上下文与GLM-4.6V对比
        prompt = r"""请将这个PDF页面转换为Markdown格式。这是数学教辅材料，请严格按照以下要求处理：

## 一、页眉页脚处理（重要）
- 完全忽略页面顶部的页眉（书名、章节名、重复的标题等）
- 完全忽略页面底部的页脚（页码、版权信息、网址等）
- 只保留正文主要内容

## 二、双栏布局处理（注释性质）
本教材采用"主内容 + 注释"的双栏设计：
- 主栏（较宽）：例题、讲解、练习题等主要教学内容
- 副栏（较窄）：注释、提示、要点说明、解题思路等辅助内容

处理方式：
1. 将注释内容嵌入到主内容的对应位置
2. 使用引用块语法（在行首添加 > 符号）标记注释内容
3. 如果注释与某段具体内容相关，将其紧跟在该内容之后
4. 如果注释是独立提示，可作为单独的引用段落

## 三、题目编号结构保护
- 完整保留所有题目编号，如：【例1】、【例2】、练习1、练习2.1等
- 保留步骤编号，如：解、证明、（1）、（2）、第一步、第二步等
- 保留章节编号和标题层级

## 四、数学公式LaTeX化
- 行内公式使用 $公式$ 格式，如 $x^2 + 2x + 1 = 0$
- 独立公式行使用 $$公式$$ 格式，如 $$\frac{a}{b} = \frac{c}{d}$$
- 使用标准LaTeX语法：
  - 分数：\frac{分子}{分母}
  - 根号：\sqrt{表达式} 或 \sqrt[n]{表达式}
  - 求和：\sum_{i=1}^{n}
  - 积分：\int_{a}^{b}
  - 极限：\lim_{x \to \infty}
  - 上标下标：x^2、a_n、x^{2n+1}
- 保持原公式的编号，如：(1)、(2)等

## 五、Markdown格式规范
1. 标题层级：使用 # ## ### #### 表示不同级别标题
2. 表格格式（严格执行）：
   - 第一行：表头，用 | 分隔各列
   - 第二行：分隔行，必须包含（|---| 或 |:---|---:|）
   - 第三行及之后：数据行
   - 确保所有行的列数完全一致
   - 示例：
     | 列1 | 列2 | 列3 |
     |-----|-----|-----|
     | 数据1 | 数据2 | 数据3 |
3. 列表：使用 - 或 1. 或 (1) 格式
4. 强调：使用 **粗体** 或 *斜体*，不要使用下划线

## 六、禁止事项（严格执行）
- 禁止输出任何思考过程或解释性文字
- 禁止使用代码块语法（``` 或 ~~~）
- 禁止将题目编号作为代码处理
- 禁止遗漏表格的分隔行（表头和数据行之间必须有 |---| 行）
- 禁止表格各行列数不一致
- 禁止遗漏任何关键信息
- 禁止自行添加或删除内容

## 七、特殊符号处理
- 绝对值：|x| 直接输出，不要用代码块
- 集合：{x | x > 0} 直接输出
- 区间：[a, b]、(a, +∞) 直接输出
- 希腊字母：α β γ θ 直接使用Unicode字符
- 数学符号：∈ ∪ ∩ ⊆ ⊂ ≠ ≤ ≥ ∞ 直接使用Unicode字符

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

                # 过滤掉  标记之间的思考内容
                import re
                # 使用正则表达式删除 <think>...</think> 及其内容
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

                # 2. 删除 <|beginofbox|> 和 <|endofbox|> 标签（保留内容）
                content = re.sub(r'<\|begin_of_box\|>', '', content)
                content = re.sub(r'<\|end_of_box\|>', '', content)

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
            page_content = self.process_page(image_path, idx)  # 使用默认的65536(64K)

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

    parser = argparse.ArgumentParser(description="使用 Qwen3-VL-8B (Ollama) 处理 PDF 文档")
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("-o", "--output", default="./output_qwen3vl", help="输出目录（默认: ./output_qwen3vl）")
    parser.add_argument("-n", "--max-pages", type=int, default=None, help="最大处理页数")
    parser.add_argument("-s", "--start-page", type=int, default=1, help="起始页码（默认: 1）")
    parser.add_argument("--api-url", default="http://localhost:11434", help="Ollama API 地址")

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.pdf_path):
        print(f"❌ 错误: PDF 文件不存在: {args.pdf_path}")
        sys.exit(1)

    # 创建处理器
    processor = Qwen3VLProcessor(api_url=args.api_url)

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
