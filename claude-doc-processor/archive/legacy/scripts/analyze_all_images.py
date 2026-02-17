#!/usr/bin/env python3
"""
分析DOCX中所有图片的脚本

用法：
python scripts/analyze_all_images.py input.docx
"""

import sys
import os
import json
import base64
from pathlib import Path
from io import BytesIO

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from docx import Document
    from docx.oxml import parse_xml
except ImportError:
    print("错误: 需要安装 python-docx")
    print("安装命令: pip install python-docx")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests")
    print("安装命令: pip install requests")
    sys.exit(1)


def extract_all_images_from_docx(docx_path: str, output_dir: str):
    """
    从DOCX提取所有图片（不过滤）
    """
    print(f"提取图片: {docx_path}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    # 打开DOCX
    doc = Document(docx_path)

    # 获取图片关系
    image_counter = 0
    extracted_images = []

    # 遍历文档中的所有图片
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            try:
                # 获取图片数据
                image_data = rel.target_part.blob
                content_type = rel.target_part.content_type

                # 检查图片尺寸
                from PIL import Image
                img = Image.open(BytesIO(image_data))
                width, height = img.size

                # 根据content_type确定扩展名
                if 'png' in content_type:
                    ext = '.png'
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'bmp' in content_type:
                    ext = '.bmp'
                else:
                    ext = '.png'

                # 生成文件名
                image_counter += 1
                filename = f"image{image_counter}{ext}"
                image_path = os.path.join(images_dir, filename)

                # 保存图片
                with open(image_path, 'wb') as f:
                    f.write(image_data)

                print(f"✓ 提取图片 {image_counter}: {filename} ({width}x{height}px, {content_type})")

                extracted_images.append({
                    'index': image_counter,
                    'filename': filename,
                    'path': image_path,
                    'width': width,
                    'height': height,
                    'size': len(image_data),
                    'content_type': content_type
                })

            except Exception as e:
                print(f"✗ 提取图片失败: {str(e)}")
                continue

    print(f"\n总计提取: {len(extracted_images)} 张图片")
    print("=" * 60)

    return extracted_images


def describe_image_with_glm(image_path: str, index: int) -> dict:
    """
    使用GLM-4V描述图片内容（通过HTTP API）
    """
    print(f"\n分析图片 {index}: {os.path.basename(image_path)}")

    try:
        # 读取图片并转换为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # 限制图片大小（如果太大就压缩提示）
        if len(image_data) > 5 * 1024 * 1024:  # 5MB
            print(f"  警告: 图片较大 ({len(image_data)/1024/1024:.2f}MB)")

        # 调用GLM-4V API
        api_key = os.environ.get("ZHIPUAI_API_KEY", "")
        if not api_key:
            raise Exception("未设置ZHIPUAI_API_KEY环境变量")

        prompt = """请详细描述这张图片的内容，包括：

1. 图片类型（如：数轴、函数图像、几何图形、表格、示意图等）
2. 具体内容和细节
3. 文字、标注、数据
4. 这是什么题目的图片（如果是试卷题目）

请简洁准确地描述，不要添加推测内容。"""

        # 构建请求数据
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "glm-4v",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }

        response = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API返回错误: {response.status_code} - {response.text}")

        result = response.json()
        description = result['choices'][0]['message']['content'].strip()
        print(f"  描述: {description[:100]}...")

        return {
            'index': index,
            'filename': os.path.basename(image_path),
            'description': description,
            'success': True
        }

    except Exception as e:
        error_msg = f"分析失败: {str(e)}"
        print(f"  ✗ {error_msg}")
        return {
            'index': index,
            'filename': os.path.basename(image_path),
            'description': error_msg,
            'success': False
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_all_images.py <input.docx>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 {input_file}")
        sys.exit(1)

    # 输出目录
    output_dir = "output_all_images_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # 步骤1: 提取所有图片（不过滤）
    print("步骤1: 提取所有图片")
    print("=" * 60)
    images = extract_all_images_from_docx(input_file, output_dir)

    # 保存图片清单
    manifest_path = os.path.join(output_dir, 'images_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=2)
    print(f"✓ 图片清单已保存: {manifest_path}")

    # 步骤2: 逐个分析图片
    print("\n步骤2: 使用GLM-4V逐个分析图片")
    print("=" * 60)

    descriptions = []
    for img_info in images:
        result = describe_image_with_glm(img_info['path'], img_info['index'])
        descriptions.append(result)

    # 保存描述结果
    descriptions_path = os.path.join(output_dir, 'image_descriptions.json')
    with open(descriptions_path, 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("分析完成！")
    print(f"总计分析: {len(descriptions)} 张图片")
    print(f"成功: {sum(1 for d in descriptions if d['success'])} 张")
    print(f"失败: {sum(1 for d in descriptions if not d['success'])} 张")
    print(f"\n结果已保存到: {output_dir}")
    print("=" * 60)

    # 打印所有描述摘要
    print("\n所有图片描述摘要:")
    print("-" * 60)
    for d in descriptions:
        status = "✓" if d['success'] else "✗"
        print(f"{status} Image {d['index']} ({d['filename']}):")
        print(f"   {d['description'][:200]}...")
        print()


if __name__ == "__main__":
    main()
