#!/usr/bin/env python3
"""
单独分析image28.png，输出详细的调试信息
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path

# API配置
API_URL = "http://192.168.100.110:9999/v1/chat/completions"
MODEL_NAME = "glm-4v"

IMAGE_PATH = "output_all_images_analysis/images/image28.png"


def compress_image(image_path: str, max_size: int = 1024) -> bytes:
    """压缩图片"""
    from PIL import Image
    from io import BytesIO

    try:
        img = Image.open(image_path)

        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        return buffer.getvalue()

    except Exception as e:
        print(f"压缩失败: {e}")
        with open(image_path, 'rb') as f:
            return f.read()


def main():
    print("=" * 60)
    print("调试分析 image28.png")
    print("=" * 60)

    # 压缩图片
    print(f"读取图片: {IMAGE_PATH}")
    compressed = compress_image(IMAGE_PATH)
    print(f"压缩后大小: {len(compressed)} bytes")

    # 转换为base64
    img_b64 = base64.b64encode(compressed).decode('utf-8')

    # 构建prompt
    prompt = """请仔细观察这张图片，并完成以下任务：

1. **描述图片内容**：详细描述图片中包含的所有元素（文字、符号、图形、图表等）

2. **判断LaTeX表达能力**：
   - 如果图片**只包含数学公式、符号、文本**，且可以完全用LaTeX数学公式表达，回答：**是**
   - 如果图片包含**图形、图表、几何图形、示意图、函数图像、统计图**等无法用LaTeX公式完全表达的视觉元素，回答：**否**

请严格按照以下JSON格式输出（不要输出其他内容）：

```json
{
  "description": "图片内容的详细描述",
  "can_be_latex": true/false,
  "reason": "为什么可以/不可以完全用LaTeX表达"
}
```

注意：
- 数学公式、分数、根号、积分等可以用LaTeX表达
- 几何图形、函数图像、示意图、统计图等**不能用**LaTeX公式完全表达
- 即使包含文字说明，只要有图形元素就应该回答"否"
"""

    # 构建请求
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}"
                    }
                }
            ]
        }
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1000
    }

    try:
        print(f"\n🔜 调用GLM-4V API...")
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        print(f"\n📥 HTTP状态码: {response.status_code}")
        print(f"📥 响应体长度: {len(response.text)} bytes")
        print(f"\n📥 原始响应内容:")
        print("=" * 60)
        print(response.text[:2000])  # 只打印前2000字符
        print("=" * 60)

        # 解析响应
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        print(f"\n📥 提取的content:")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # 尝试解析JSON
        import re

        # 方法1: 提取代码块中的JSON
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print(f"\n✓ 提取到JSON代码块")
        else:
            # 方法2: 直接使用整个内容
            json_str = content.strip()
            print(f"\n⚠️  未找到JSON代码块，使用整个内容")

        print(f"\n📋 JSON字符串:")
        print("=" * 60)
        print(json_str[:500])
        print("=" * 60)

        # 尝试解析
        try:
            analysis = json.loads(json_str)
            print(f"\n✅ JSON解析成功！")
            print(f"Description: {analysis.get('description', '')[:100]}...")
            print(f"Can be LaTeX: {analysis.get('can_be_latex')}")
            print(f"Reason: {analysis.get('reason', '')[:100]}...")
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON解析失败: {e}")
            print(f"   错误位置: {e.pos if hasattr(e, 'pos') else 'unknown'}")
            print(f"   错误行/列: {e.lineno}, {e.colno if hasattr(e, 'colno') else 'unknown'}")

            # 尝试手动提取字段
            print(f"\n🔧 尝试手动提取字段...")

            desc_match = re.search(r'"description"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', json_str, re.DOTALL)
            latex_match = re.search(r'"can_be_latex"\s*:\s*(true|false)', json_str)
            reason_match = re.search(r'"reason"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', json_str, re.DOTALL)

            print(f"   description match: {bool(desc_match)}")
            print(f"   can_be_latex match: {bool(latex_match)}")
            print(f"   reason match: {bool(reason_match)}")

            if desc_match and latex_match and reason_match:
                desc = desc_match.group(1)
                can_latex = latex_match.group(1) == 'true'
                reason = reason_match.group(1)

                print(f"\n✅ 手动提取成功！")
                print(f"Description: {desc[:100]}...")
                print(f"Can be LaTeX: {can_latex}")
                print(f"Reason: {reason[:100]}...")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
