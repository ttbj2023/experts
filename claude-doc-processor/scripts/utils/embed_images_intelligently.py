#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片智能嵌入工具

使用GLM-4.6V-Flash分析Markdown内容和图片，将图片插入到正确的位置
"""

import os
import base64
import json
import re
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageEmbedder:
    """图片智能嵌入器 - 使用GLM-4.6V-Flash"""

    def __init__(self, api_url: str = "http://192.168.100.110:9999/api/v1/chat"):
        self.api_url = api_url
        self.model = "glm-4.6v-flash"

    def embed_images(self, md_path: str, images_dir: str, output_path: str):
        """
        智能嵌入图片到Markdown中（分批处理所有图片）

        Args:
            md_path: Markdown文件路径
            images_dir: 图片目录路径
            output_path: 输出文件路径
        """
        import requests

        # 读取Markdown内容
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 获取所有图片
        images = []
        if os.path.exists(images_dir):
            image_files = sorted([f for f in os.listdir(images_dir)
                                if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))],
                               key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)

            for img_file in image_files:
                img_path = os.path.join(images_dir, img_file)
                images.append({
                    'filename': img_file,
                    'path': img_path
                })

        logger.info(f"找到 {len(images)} 张图片")
        logger.info(f"Markdown内容长度: {len(md_content)} 字符")

        # 分批处理（每批10张图片）
        batch_size = 10
        total_batches = (len(images) + batch_size - 1) // batch_size

        logger.info(f"将分 {total_batches} 批处理图片...")

        current_md = md_content

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(images))
            batch_images = images[start_idx:end_idx]

            logger.info(f"\n处理第 {batch_idx + 1}/{total_batches} 批 (图片 {start_idx + 1}-{end_idx})")

            # 构建提示词
            prompt = f"""你是一个专业的文档处理助手。你需要将提供的图片嵌入到Markdown文档的正确位置。

## 任务说明

1. **分析内容**: 仔细阅读Markdown文档，理解其内容结构
2. **识别图片**: 分析每张图片的内容（几何图形、函数图象、示意图等）
3. **理解上下文**: 在文档中找到提到该图片的位置
   - 寻找类似"如图"、"如图所示"、"见图"等关键词
   - 寻找题号后面缺少图片的地方
4. **智能嵌入**: 将图片插入到最合适的位置

## 嵌入规则

1. **精确定位**: 在提到的图片下方插入，使用标准Markdown语法
   ```markdown
   ![图片描述](images/图片文件名)
   ```

2. **描述要求**: 图片alt文本应简洁描述图片内容
   - 例如：`![数轴图](images/image1.png)`
   - 例如：`![几何图形](images/image4.png)`

3. **避免重复**:
   - 如果已经有"数轴图：-3 -2 -1 0 1 2 3 P"这样的文字描述，在其后插入图片
   - 如果有"> [图示：...]"这样的说明，在其后插入图片

4. **图片顺序**: 按照图片编号顺序插入（image1, image4, image5...）

5. **特殊情况**:
   - 如果某些图片没有明确提及，放在对应题号后面
   - 不要删除原有内容，只插入图片引用

6. **保留已有图片**: 如果文档中已经包含某些图片的引用，不要重复添加

## 输出要求

**只返回处理后的完整Markdown文档内容**，不要添加任何解释、注释或额外的文字。

开始处理：

---

{current_md}

---

本批需要嵌入的图片：
{', '.join([img['filename'] for img in batch_images])}

请分析文档内容和这些图片，将每张图片插入到正确的位置，然后返回完整的Markdown文档。
"""

            # 构建请求数据
            input_data = [
                {
                    "type": "text",
                    "content": prompt
                }
            ]

            # 添加本批图片
            for i, img in enumerate(batch_images):
                try:
                    with open(img['path'], 'rb') as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')

                    input_data.append({
                        "type": "image",
                        "data_url": f"data:image/png;base64,{img_base64}"
                    })
                    logger.info(f"  添加图片 {i+1}/{len(batch_images)}: {img['filename']}")
                except Exception as e:
                    logger.error(f"读取图片失败: {img['filename']}, {str(e)}")

            # 调用API
            request_data = {
                "model": self.model,
                "system_prompt": "你是一个专业的文档处理助手，擅长将图片嵌入到Markdown文档的正确位置。只返回处理后的Markdown，不要添加任何解释。",
                "input": input_data
            }

            try:
                logger.info(f"正在调用GLM-4.6V-Flash API (批次 {batch_idx + 1}/{total_batches})...")
                response = requests.post(
                    self.api_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=300  # 5分钟超时
                )

                if response.status_code == 200:
                    result = response.json()

                    # 解析响应
                    if 'output' in result and isinstance(result['output'], list):
                        message_content = None
                        for item in result['output']:
                            if item.get('type') == 'message':
                                message_content = item.get('content', '')
                                break

                        if message_content:
                            # 更新当前Markdown内容
                            current_md = message_content

                            # 统计当前已嵌入的图片数量
                            embedded_count = current_md.count('![')
                            logger.info(f"  ✓ 批次 {batch_idx + 1} 完成，已嵌入 {embedded_count} 张图片")
                        else:
                            logger.warning(f"批次 {batch_idx + 1}: API响应中没有找到message内容")
                    else:
                        logger.warning(f"批次 {batch_idx + 1}: API响应格式异常")
                else:
                    logger.error(f"批次 {batch_idx + 1}: API调用失败: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")

            except requests.exceptions.Timeout:
                logger.error(f"批次 {batch_idx + 1}: API调用超时")
            except Exception as e:
                logger.error(f"批次 {batch_idx + 1}: 处理异常: {str(e)}")

        # 保存最终结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(current_md)

        logger.info(f"\n✅ 所有批次处理完成！")
        logger.info(f"   输出文件: {output_path}")

        # 统计最终嵌入的图片数量
        embedded_count = current_md.count('![')
        logger.info(f"   总共嵌入: {embedded_count}/{len(images)} 张图片")

        return True


def main():
    import sys

    if len(sys.argv) < 3:
        print("用法: python3 embed_images_intelligently.py <md_file> <images_dir> [output_file]")
        print("示例: python3 embed_images_intelligently.py document.md images document_embedded.md")
        sys.exit(1)

    md_file = sys.argv[1]
    images_dir = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else md_file.replace('.md', '_embedded.md')

    if not os.path.exists(md_file):
        print(f"错误: Markdown文件不存在: {md_file}")
        sys.exit(1)

    if not os.path.exists(images_dir):
        print(f"错误: 图片目录不存在: {images_dir}")
        sys.exit(1)

    print("=" * 60)
    print("图片智能嵌入工具")
    print("=" * 60)
    print(f"输入文件: {md_file}")
    print(f"图片目录: {images_dir}")
    print(f"输出文件: {output_file}")
    print("=" * 60)

    embedder = ImageEmbedder()
    success = embedder.embed_images(md_file, images_dir, output_file)

    if success:
        print("\n✅ 处理成功！")
        print(f"输出文件: {output_file}")
    else:
        print("\n❌ 处理失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
