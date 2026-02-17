#!/usr/bin/env python3
"""
使用DeepSeek进行占位符与图片的语义匹配

输入：
- 占位符列表（从Markdown中提取）
- 图片描述列表（GLM-4V生成）

输出：
- 匹配结果：{placeholder_index: image_filename}
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-62f31b03e22048799beefff7cae0dfc3")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def deepseek_match(placeholders: List[Dict], images: List[Dict]) -> Dict[int, str]:
    """
    使用DeepSeek进行语义匹配

    Args:
        placeholders: 占位符列表
            [{
                "index": 0,
                "type": "数轴示意图",
                "description": "数轴示意图，从左到右依次标注P、Q、R、S..."
            }]
        images: 图片描述列表
            [{
                "filename": "image1.png",
                "description": "图片展示了一条水平向右延伸的数轴..."
            }]

    Returns:
        匹配结果: {placeholder_index: image_filename}
    """

    # 构建prompt
    prompt = """你是一个智能文档处理助手，负责将图片占位符与实际图片进行语义匹配。

## 任务说明
我会给你：
1. 一组图片占位符的描述（从文档中提取）
2. 一组实际图片的描述（由GLM-4V视觉模型生成）

请你**仔细分析每个占位符的描述和每个图片的描述**，找出它们之间的语义对应关系，然后将占位符匹配到最合适的图片。

## 匹配原则
1. **语义相似度**：占位符描述的内容应该与图片描述的内容高度一致
2. **细节匹配**：关键元素（如形状、标注、文字、数量等）必须匹配
3. **一一对应**：每个占位符匹配一个唯一的图片，每个图片只能匹配一个占位符
4. **精确匹配**：如果找不到合适的匹配，就返回null，不要强行匹配

## 匹配要求
- 严格按照JSON格式输出
- 确保匹配的准确性，宁缺毋滥
- 如果多个图片都与一个占位符相似，选择最匹配的那个

## 输入数据

### 占位符列表：
"""

    # 添加占位符
    for p in placeholders:
        idx = p.get('index', p.get('id', '?'))
        ptype = p.get('type', '未知类型')
        desc = p.get('description', '')
        prompt += f"\n**占位符 {idx}**\n"
        prompt += f"- 类型: {ptype}\n"
        prompt += f"- 描述: {desc}\n"

    prompt += "\n\n### 图片描述列表：\n"

    # 添加图片描述
    for img in images:
        filename = img.get('image_file', img.get('filename', 'unknown'))
        desc = img.get('description', '')
        prompt += f"\n**{filename}**\n"
        prompt += f"- 描述: {desc}\n"

    prompt += """

## 输出格式

请严格按照以下JSON格式输出（不要输出其他内容）：

```json
{
  "matches": [
    {
      "placeholder_index": 0,
      "image_filename": "image5.png",
      "confidence": "高",
      "reason": "占位符描述'数轴示意图'与图片描述'水平向右延伸的数轴'完全匹配，且都提到了点P、Q、R、S及标注-a、a、1/a"
    }
  ],
  "unmatched_placeholders": [],
  "unmatched_images": []
}
```

说明：
- `placeholder_index`: 占位符的索引（从0开始）
- `image_filename`: 匹配的图片文件名
- `confidence`: 匹配置信度（高/中/低）
- `reason`: 匹配理由（简短说明）
- `unmatched_placeholders`: 未匹配到的占位符索引列表
- `unmatched_images`: 未匹配到的图片文件名列表

现在请开始匹配：
"""

    # 调用DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }

    try:
        print(f"🔜 调用DeepSeek API进行语义匹配...")
        print(f"   - 占位符数量: {len(placeholders)}")
        print(f"   - 图片数量: {len(images)}")

        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        # 提取content
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        print(f"\n📥 DeepSeek响应:")
        print(content)

        # 解析JSON
        import re
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content.strip()

        match_result = json.loads(json_str)

        # 转换为简单的映射格式
        mapping = {}
        for m in match_result.get("matches", []):
            idx = m.get("placeholder_index")
            filename = m.get("image_filename")
            if idx is not None and filename:
                mapping[idx] = filename

        print(f"\n✅ 匹配完成: {len(mapping)}/{len(placeholders)} 个占位符成功匹配")

        if match_result.get("unmatched_placeholders"):
            print(f"⚠️  未匹配的占位符: {match_result['unmatched_placeholders']}")

        if match_result.get("unmatched_images"):
            print(f"⚠️  未匹配的图片: {match_result['unmatched_images']}")

        return mapping, match_result

    except Exception as e:
        print(f"❌ DeepSeek匹配失败: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}


def load_latex_analysis(json_file: str) -> List[Dict]:
    """加载LaTeX分析结果，提取图片描述"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    images = []
    for img in data.get('images', []):
        images.append({
            'image_file': img.get('image_file'),
            'description': img.get('description', ''),
            'can_be_latex': img.get('can_be_latex')
        })

    return images


def extract_placeholders_from_md(md_file: str) -> List[Dict]:
    """从Markdown文件中提取占位符"""
    placeholders = []

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    pattern = r'<!--\s*IMAGE_PLACEHOLDER\s+(.*?)-->'
    matches = re.findall(pattern, content, re.DOTALL)

    for idx, match in enumerate(matches):
        # 提取type和description
        type_match = re.search(r'type:\s*(.+?)(?:\n|$)', match)
        desc_match = re.search(r'description:\s*(.+?)(?:-->|$)', match, re.DOTALL)

        ptype = type_match.group(1).strip() if type_match else '未知'
        desc = desc_match.group(1).strip() if desc_match else ''

        placeholders.append({
            'index': idx,
            'type': ptype,
            'description': desc
        })

    return placeholders


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='使用DeepSeek进行占位符与图片的语义匹配')
    parser.add_argument('--md-file', required=True, help='带占位符的Markdown文件')
    parser.add_argument('--latex-analysis', required=True, help='LaTeX分析JSON文件')
    parser.add_argument('--output', default='deepseek_match_result.json', help='输出文件')

    args = parser.parse_args()

    print("=" * 60)
    print("DeepSeek语义匹配")
    print("=" * 60)

    # 提取占位符
    print(f"\n📄 读取Markdown文件: {args.md_file}")
    placeholders = extract_placeholders_from_md(args.md_file)
    print(f"✓ 找到 {len(placeholders)} 个占位符")

    # 加载图片描述
    print(f"\n📸 读取LaTeX分析文件: {args.latex_analysis}")
    images = load_latex_analysis(args.latex_analysis)
    print(f"✓ 加载 {len(images)} 张图片的描述")

    # DeepSeek匹配
    print(f"\n🤖 启动DeepSeek语义匹配...")
    mapping, detailed_result = deepseek_match(placeholders, images)

    # 保存结果
    output = {
        'mapping': mapping,
        'detailed_result': detailed_result,
        'summary': {
            'total_placeholders': len(placeholders),
            'total_images': len(images),
            'matched': len(mapping),
            'unmatched_placeholders': len(placeholders) - len(mapping),
            'unmatched_images': len(images) - len(mapping)
        }
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 结果已保存到: {args.output}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
