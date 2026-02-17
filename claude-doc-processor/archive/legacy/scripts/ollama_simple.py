#!/usr/bin/env python3
"""
直接用 Ollama 读取并处理 Markdown，不改变原有格式
"""

import sys
import json
import requests

def process_with_ollama(md_file, model="gpt-oss:20b"):
    """
    使用 Ollama 直接处理 Markdown 文件

    Args:
        md_file: Markdown 文件路径
        model: Ollama 模型名称
    """
    # 读取原始内容
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"📄 文件: {md_file}")
    print(f"   大小: {len(content)} 字符")
    print(f"   模型: {model}")

    # 简单调用：让模型总结或优化内容
    prompt = f"""请阅读以下 Markdown 内容并直接输出，不要改变任何格式：

{content}

要求：
- 保持原有的 LaTeX 公式格式
- 保持原有的表格结构
- 保持原有的标题层级
- 如果有明显的格式错误，可以修复
- 不要添加任何解释性文字
"""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if 'message' in result:
                processed_content = result['message']['content']
                print(f"\n✅ 处理完成！")
                print(f"   输出预览（前200字符）：")
                print(processed_content[:200])
                return processed_content
            else:
                print("❌ 未返回内容")
                return None
        else:
            print(f"❌ API 错误: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 scripts/ollama_simple.py <md_file>")
        print("示例: python3 scripts/ollama_simple.py output_xxx.md")
        sys.exit(1)

    result = process_with_ollama(sys.argv[1])

    if result:
        # 保存到 _processed.md
        output_file = sys.argv[1].replace('.md', '_processed.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n📄 已保存: {output_file}")
