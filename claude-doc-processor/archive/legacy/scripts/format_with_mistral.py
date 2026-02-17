#!/usr/bin/env python3
"""
使用Mistral AI格式化GLM-4.6V输出的Markdown
每日免费90万次调用
"""

import os
import sys
import json
import time
import requests
from pathlib import Path


def format_markdown_with_mistral(md_file, api_key=None):
    """
    使用Mistral AI格式化GLM-4.6V输出的Markdown文件

    Args:
        md_file: Markdown文件路径
        api_key: Mistral API密钥（如果未设置则提示用户）

    Returns:
        格式化后的内容（字符串），如果失败返回None
    """
    # 检查API密钥
    if api_key is None:
        env_key = os.getenv('MISTRAL_API_KEY')
        if not env_key or env_key == 'None':
            print("🔑 请先设置Mistral API密钥：")
            print("   方法1：export MISTRAL_API_KEY='your_api_key_here'")
            print("   方法2：在脚本中添加密钥文件：")
            print("           echo 'your_api_key_here' > .mistral_api_key")
            print("\n   获取密钥：https://console.mistral.ai/")
            return None

    # 读取原始内容
    print(f"📄 读取文件: {md_file}")
    with open(md_file, 'r', encoding='utf-8') as f:
        original_content = f.read()

    print(f"   原始内容: {len(original_content)} 字符")

    # 调用Mistral API
    url = "https://api-inference.modelscope.cn/v1"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = f"""你是一个专业的文档格式化助手。请将用户提供的PDF识别内容（Markdown格式）重新整理为规范、美观的格式。

## 核心格式要求

### 1. 表格格式（最关键）

必须严格遵循以下Markdown表格格式：

| 列1标题 | 列2标题 | 列3标题 | 列4标题 |
| :--- | :--- | :--- | :--- |
| 数据1 | 数据2 | 数据3 | 数据4 |

**绝对规则**：
- 第1行：表头行，用 `|` 分隔各列
- 第2行：分隔行，用 `|---|` 或 `|:---|` 分隔
- 第3行及以后：数据行，用 `|` 分隔各数据
- **每行结尾**：必须有 `|` 符号
- **列对齐**：每个 `|` 后面都要有内容

### 2. 数学公式LaTeX格式

#### 行内公式
- 使用 `$...$` 格式
- 正确示例：$x_1, x_2, \dots, x_n$

#### 块级公式
- 使用 `$$...$$` 格式独占一行
- 正确示例：
  $$\\overline{x} = \\frac{x_1 + x_2 + \\dots + x_n}{n}$$

### 3. 标题层级

- 一级标题：`# 标题`
- 二级标题：`## 标题`
- 三级标题：`### 标题`

### 4. 列表格式

- 无序列表：使用 `- 项目`
- 有序列表：使用 `1. 项目`

### 5. 粗体格式

- 使用 `**文本** 表示粗体

## 输出要求

1. 直接输出Markdown内容，不要添加解释
2. 表格必须完整：表头、分隔行、数据行完整
3. 公式符号清晰：$ 和 \ 不要混用
4. 保留所有信息，只改格式

请严格按照这些格式要求重新格式化以下内容：

{original_content}
"""

    payload = {
        "model": "mistralai/Mistral-Small-Instruct-2409",
        "messages": [
            {
                "role": "user",
                "content": prompt + "\n\n" + original_content
            }
        ],
        "stream": False,
        "temperature": 0.1,
        "max_tokens": 16384
    }

    print(f"\n🔄 调用Mistral AI格式化...")
    print(f"   API: {url}")
    print(f"   模型: mistralai/Mistral-Small-Instruct-2409")
    print(f"   最大tokens: 16384")

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                formatted_content = result['choices'][0]['message']['content']
                print(f"\n✅ 格式化成功！")
                print(f"   Prompt tokens: {result.get('usage', {}).get('prompt_tokens', 'N/A')}")
                print(f"   Completion tokens: {result.get('usage', {}).get('completion_tokens', 'N/A')}")
                print(f"\n   格式化内容预览（前200字符）：")
                print(formatted_content[:200])
                return formatted_content
            else:
                print(f"\n❌ 格式化失败：未返回内容")
                return None
        elif response.status_code == 401:
            print(f"\n❌ API密钥无效或达到每日限额（401）")
            print(f"   请检查：")
            print(f"   1. API密钥是否正确设置")
            print(f"   2. 是否已达到每日限额（90万次/天）")
            print(f"\n   获取密钥：https://console.mistral.ai/")
            return None
        else:
            print(f"\n❌ API调用失败：{response.status_code}")
            print(f"   错误信息：{response.text[:200] if response.text else 'N/A'}")
            return None

    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时（>180秒）")
        return None
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return None


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 scripts/format_with_mistral.py <input.md> [api_key]")
        print("\n参数说明：")
        print("  <input.md>: GLM-4.6V输出的Markdown文件路径")
        print("  [api_key]: Mistral API密钥（可选，未设置则提示）")
        print("\n功能：")
        print("  - 使用Mistral AI格式化Markdown内容")
        print("  - 每日免费90万次调用")
        print("  - 自动修复表格、公式、列表格式")
        print("\n示例：")
        print("   python3 scripts/format_with_mistral.py page_002.md")
        print("   python3 scripts/format_with_mistral.py page_002.md your_api_key")
        sys.exit(1)

    md_file = sys.argv[1] if len(sys.argv) > 1 else None

    if not md_file:
        print(f"\n❌ 错误：未指定Markdown文件")
        sys.exit(1)

    if not Path(md_file).exists():
        print(f"\n❌ 错误：Markdown文件不存在: {md_file}")
        sys.exit(1)

    # 格式化
    formatted_content = format_markdown_with_mistral(md_file)

    if formatted_content:
        # 保存格式化后的文件
        output_file = str(Path(md_file).with_suffix('_formatted.md'))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        print(f"\n✅ 格式化完成！")
        print(f"   📄 输出文件: {output_file}")
        print(f"\n   📊 原始文件: {md_file}")
        print(f"\n   💡 提示：可以使用Typora等工具查看格式化效果")
    else:
        print("\n❌ 格式化失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
