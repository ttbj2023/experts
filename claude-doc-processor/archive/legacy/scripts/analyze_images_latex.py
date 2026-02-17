#!/usr/bin/env python3
"""
使用GLM-4V分析图片是否可以完全用LaTeX表达

遍历指定目录下的所有图片，调用GLM-4V API进行分析，
判断图片内容是否可以完全用LaTeX数学公式表达。
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

# 图片目录
IMAGE_DIR = "output_all_images_analysis/images"

# 输出文件
OUTPUT_FILE = "image_latex_analysis.json"


def compress_image(image_path: str, max_size: int = 1024) -> bytes:
    """压缩图片以减少token消耗"""
    from PIL import Image
    from io import BytesIO

    try:
        img = Image.open(image_path)

        # 计算新尺寸
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 转换为RGB
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

        # 压缩为JPEG
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        return buffer.getvalue()

    except Exception as e:
        print(f"压缩图片失败 {image_path}: {e}")
        # 降级：读取原始数据
        with open(image_path, 'rb') as f:
            return f.read()


def analyze_image_with_glm(image_path: str, image_index: int) -> dict:
    """使用GLM分析图片是否可以用LaTeX表达"""

    print(f"\n{'='*60}")
    print(f"正在分析: {os.path.basename(image_path)} (图片 {image_index}/30)")
    print(f"{'='*60}")

    # 读取图片信息
    img_path = Path(image_path)
    file_size = img_path.stat().st_size
    print(f"文件大小: {file_size} bytes")

    # 压缩图片
    compressed = compress_image(image_path)
    print(f"压缩后: {len(compressed)} bytes")

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
        "max_tokens": 2000
    }

    try:
        # 调用API
        print(f"🔜 正在调用GLM-4V API...")
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        # 解析响应
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        print(f"📥 GLM响应:")
        print(content)

        # 提取JSON
        import re
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = content.strip()

        # 解析JSON（处理LaTeX转义问题）
        try:
            # 先尝试直接解析
            analysis = json.loads(json_str)
        except json.JSONDecodeError as e:
            # 如果失败，尝试修复LaTeX转义问题
            print(f"⚠️  JSON解析失败，尝试修复LaTeX转义...")
            print(f"   原始JSON前200字符: {json_str[:200]}")

            # 方法1: 使用正则替换LaTeX中的反斜杠
            # 将 \\ 替换为 \\\\ (JSON中的\\表示一个\)
            import re

            # 先处理常见的LaTeX模式
            json_str_fixed = json_str

            # 修复 \frac{a}{b} 这类模式 - 在JSON字符串中应该是 \\frac
            # 但GLM可能直接输出了 \frac，导致解析失败
            # 我们需要将其转换为有效的JSON字符串

            # 尝试使用demjson或者手动解析
            try:
                # 使用python的json.loads with strict=False
                analysis = json.loads(json_str_fixed, strict=False)
            except:
                # 如果还是失败，尝试eval（不安全但能处理简单情况）
                try:
                    # 移除JSON字符串外的换行和空格
                    json_str_fixed = json_str_fixed.replace('\n', ' ')
                    # 使用ast.literal_eval更安全
                    import ast
                    analysis = ast.literal_eval(json_str_fixed)
                except:
                    # 最后的手段：手动提取字段（改进版，支持中文和换行）
                    print(f"⚠️  使用正则提取字段...")

                    # 更宽松的正则，允许换行和中文
                    desc_match = re.search(r'"description"\s*:\s*"((?:[^"\\]|\\.)*)"', json_str, re.DOTALL)
                    latex_match = re.search(r'"can_be_latex"\s*:\s*(true|false)', json_str)
                    reason_match = re.search(r'"reason"\s*:\s*"((?:[^"\\]|\\.)*)"', json_str, re.DOTALL)

                    print(f"   description match: {bool(desc_match)}")
                    print(f"   can_be_latex match: {bool(latex_match)}")
                    print(f"   reason match: {bool(reason_match)}")

                    if desc_match and latex_match and reason_match:
                        # 手动构建分析结果，处理转义字符
                        desc = desc_match.group(1)
                        # 处理转义序列
                        desc = desc.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')

                        can_latex = latex_match.group(1) == 'true'

                        reason = reason_match.group(1)
                        reason = reason.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')

                        analysis = {
                            'description': desc,
                            'can_be_latex': can_latex,
                            'reason': reason
                        }

                        print(f"✅ 手动提取成功！")
                        print(f"   Description: {desc[:80]}...")
                        print(f"   Can be LaTeX: {can_latex}")
                        print(f"   Reason: {reason[:80]}...")
                    else:
                        raise ValueError("无法从响应中提取有效字段")

        # 添加图片信息
        analysis['image_file'] = os.path.basename(image_path)
        analysis['image_path'] = image_path
        analysis['file_size_bytes'] = file_size
        analysis['compressed_size_bytes'] = len(compressed)

        # 打印结果
        latex_status = "✅ 可以" if analysis['can_be_latex'] else "❌ 不可以"
        print(f"\n结果: {latex_status} 用LaTeX完全表达")
        print(f"原因: {analysis['reason']}")

        return analysis

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return {
            'image_file': os.path.basename(image_path),
            'image_path': image_path,
            'file_size_bytes': file_size,
            'compressed_size_bytes': len(compressed),
            'description': '',
            'can_be_latex': None,
            'reason': f'分析失败: {str(e)}',
            'error': True
        }


def main():
    """主函数"""

    print("=" * 60)
    print("GLM-4V 图片LaTeX表达能力分析")
    print("=" * 60)
    print(f"图片目录: {IMAGE_DIR}")
    print(f"输出文件: {OUTPUT_FILE}")
    print("=" * 60)

    # 获取所有图片
    image_dir = Path(IMAGE_DIR)
    if not image_dir.exists():
        print(f"❌ 错误: 图片目录不存在: {IMAGE_DIR}")
        sys.exit(1)

    # 按文件名排序
    image_files = sorted(image_dir.glob("*.png"), key=lambda x: x.name)

    if not image_files:
        print(f"❌ 错误: 目录中没有找到PNG图片")
        sys.exit(1)

    print(f"✓ 找到 {len(image_files)} 张图片")
    print()

    # 分析所有图片
    results = []
    for idx, image_path in enumerate(image_files, start=1):
        result = analyze_image_with_glm(str(image_path), idx)
        results.append(result)

    # 统计结果
    can_latex = [r for r in results if r.get('can_be_latex') == True]
    cannot_latex = [r for r in results if r.get('can_be_latex') == False]
    failed = [r for r in results if r.get('can_be_latex') is None]

    print("\n" + "=" * 60)
    print("分析完成统计")
    print("=" * 60)
    print(f"总图片数: {len(results)}")
    print(f"✅ 可以用LaTeX表达: {len(can_latex)} 张")
    print(f"❌ 不可以用LaTeX表达: {len(cannot_latex)} 张")
    print(f"⚠️  分析失败: {len(failed)} 张")
    print("=" * 60)

    # 列出可以/不可以的图片
    if can_latex:
        print(f"\n✅ 可以用LaTeX表达的图片 ({len(can_latex)}张):")
        for r in can_latex:
            print(f"  - {r['image_file']}")

    if cannot_latex:
        print(f"\n❌ 不可以用LaTeX表达的图片 ({len(cannot_latex)}张):")
        for r in cannot_latex:
            print(f"  - {r['image_file']}")

    # 保存结果
    output = {
        'total': len(results),
        'can_be_latex': len(can_latex),
        'cannot_be_latex': len(cannot_latex),
        'failed': len(failed),
        'images': results
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 结果已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
