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
import re


def fix_latex_escapes(text):
    """
    修复 LaTeX 公式中的常见转义问题

    Args:
        text: 原始文本

    Returns:
        修复后的文本
    """
    # 修复 \frac{a}{b} 类型的转义问题（例如 \frac{1}{n} -> \frac{1}{n}）
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\\frac{\1}{\2}', text)

    # 修复 \overline{x} 等单参数命令
    text = re.sub(r'\\overline\{([^}]+)\}', r'\\overline{\1}', text)
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'\\sqrt{\1}', text)

    # 修复其他常见的 LaTeX 命令
    latex_commands = ['sum', 'int', 'prod', 'lim', 'max', 'min', 'sin', 'cos', 'tan', 'log', 'ln']
    for cmd in latex_commands:
        text = re.sub(rf'\\{cmd}\_', rf'\\{cmd}_', text)

    return text


def format_markdown_with_mistral(md_file, api_key=None):
    """
    使用Mistral AI格式化GLM-4.6V输出的Markdown文件

    Args:
        md_file: Markdown文件路径
        api_key: Mistral API密钥（如果未设置则提示用户）

    Returns:
        格式化后的内容（字符串），如果失败返回None
    """
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

    # 使用 raw string 来处理 LaTeX 反斜杠
    prompt = r"""你是一个专业的文档格式化助手。请将用户提供的PDF识别内容（Markdown格式）重新整理为规范、美观的格式。

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
- 正确示例：$$\overline{x} = \frac{x_1 + x_2 + \dots + x_n}{n}$$

### 3. 标题层级

- 一级标题：`# 标题`
- 二级标题：`## 标题`
- 三级标题：`### 标题`

### 4. 列表格式

- 无序列表：使用 `- 项目`
- 有序列表：使用 `1. 项目`

### 5. 粗体格式

- 使用 `**文本**` 表示粗体

## 输出要求

1. **直接输出Markdown内容，不要添加解释**
2. **不要使用代码块包裹（不要用 ```markdown ... ```）**
3. 表格必须完整：表头、分隔行、数据行完整
4. 公式符号清晰：LaTeX 使用 `\\frac{a}{b}`、`\\overline{x}` 格式
5. 保留所有信息，只改格式

请严格按照这些格式要求重新格式化以下内容：

""" + original_content

    payload = {
        "model": "mistralai/Mistral-Small-Instruct-2409",
        "messages": [
            {
                "role": "user",
                "content": prompt
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
        response = requests.post(f"{url}/chat/completions", headers=headers, json=payload, timeout=180)
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                formatted_content = result['choices'][0]['message']['content']

                # 移除可能存在的代码块标记
                # 移除开头的 ```markdown 或 ```
                formatted_content = re.sub(r'^```markdown\n', '', formatted_content)
                formatted_content = re.sub(r'^```\n', '', formatted_content)
                # 移除结尾的 ```
                formatted_content = re.sub(r'\n```$', '', formatted_content)
                formatted_content = formatted_content.strip()

                # 修复 LaTeX 公式中的转义问题
                formatted_content = fix_latex_escapes(formatted_content)

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
    if len(sys.argv) < 2:
        print("用法: python3 scripts/format_with_mistral_fixed.py <input.md> <api_key>")
        print("\n参数说明：")
        print("  <input.md>: GLM-4.6V输出的Markdown文件路径")
        print("  <api_key>: Mistral API密钥")
        print("\n功能：")
        print("  - 使用Mistral AI格式化Markdown内容")
        print("  - 每日免费90万次调用")
        print("  - 自动修复表格、公式、列表格式")
        print("\n示例：")
        print('   python3 scripts/format_with_mistral_fixed.py page_002.md "ms-9016c87d-920e-4134-a035-e15670e03d10"')
        sys.exit(1)

    md_file = sys.argv[1]

    if len(sys.argv) < 3:
        print(f"\n❌ 错误：未指定API密钥")
        sys.exit(1)

    api_key = sys.argv[2]

    if not Path(md_file).exists():
        print(f"\n❌ 错误：Markdown文件不存在: {md_file}")
        sys.exit(1)

    # 格式化
    formatted_content = format_markdown_with_mistral(md_file, api_key)

    if formatted_content:
        # 保存格式化后的文件
        md_path = Path(md_file)
        output_file = str(md_path.parent / f"{md_path.stem}_formatted.md")
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
