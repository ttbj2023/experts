#!/usr/bin/env python3
"""
使用本地 LLM 格式化 GLM-4.6V 输出的 Markdown
支持：Qwen、GLM、DeepSeek 等本地部署的模型
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
    """
    # 修复各种常见的 LaTeX 格式问题
    # 1. 修复 \frac{a}{b} 格式
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\\frac{\1}{\2}', text)

    # 2. 修复 \overline{x} 等单参数命令
    text = re.sub(r'\\overline\{([^}]+)\}', r'\\overline{\1}', text)
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'\\sqrt{\1}', text)

    return text


def format_markdown_with_local_llm(md_file, api_url="http://192.168.100.110:9999",
                                     model="Qwen/Qwen2.5-72B-Instruct"):
    """
    使用本地 LLM 格式化 GLM-4.6V 输出的 Markdown 文件

    Args:
        md_file: Markdown 文件路径
        api_url: 本地 LLM API 地址
        model: 模型名称

    Returns:
        格式化后的内容（字符串），如果失败返回 None
    """
    # 读取原始内容
    print(f"📄 读取文件: {md_file}")
    with open(md_file, 'r', encoding='utf-8') as f:
        original_content = f.read()

    print(f"   原始内容: {len(original_content)} 字符")

    # 调用本地 LLM API
    url = api_url.rstrip('/')
    headers = {
        "Content-Type": "application/json"
    }

    # 使用 raw string 来处理 LaTeX 反斜杠
    prompt = r"""你是一个专业的文档格式化助手。请将用户提供的PDF识别内容（Markdown格式）重新整理为规范、美观的格式。

**重要提醒：直接输出格式化后的Markdown内容，不要输出你的思考过程、分析步骤或解释性文字。**

## 核心格式要求

### 1. 表格格式（最关键）

必须严格遵循以下 Markdown 表格格式：

| 列1标题 | 列2标题 | 列3标题 | 列4标题 |
| :--- | :--- | :--- | :--- |
| 数据1 | 数据2 | 数据3 | 数据4 |

**绝对规则**：
- 第1行：表头行，用 `|` 分隔各列
- 第2行：分隔行，用 `|---|` 或 `|:---|` 分隔
- 第3行及以后：数据行，用 `|` 分隔各数据
- **每行结尾**：必须有 `|` 符号
- **列对齐**：每个 `|` 后面都要有内容

### 2. 数学公式 LaTeX 格式

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

1. **直接输出 Markdown 内容，不要添加任何解释或思考过程**
2. **不要使用代码块包裹（不要用 ```markdown ... ```）**
3. 表格必须完整：表头、分隔行、数据行完整
4. 公式符号清晰：LaTeX 使用 `\\frac{a}{b}`、`\\overline{x}` 格式
5. 保留所有信息，只改格式

现在直接输出格式化后的内容：

""" + original_content

    payload = {
        "model": model,
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

    print(f"\n🔄 调用本地 LLM 格式化...")
    print(f"   API: {url}")
    print(f"   模型: {model}")
    print(f"   最大tokens: 16384")

    start_time = time.time()
    try:
        response = requests.post(f"{url}/v1/chat/completions",
                           headers=headers, json=payload, timeout=180)
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                formatted_content = result['choices'][0]['message']['content']

                # 移除可能存在的代码块标记
                formatted_content = re.sub(r'^```markdown\n', '', formatted_content)
                formatted_content = re.sub(r'^```\n', '', formatted_content)
                formatted_content = re.sub(r'\n```$', '', formatted_content)
                formatted_content = formatted_content.strip()

                # 移除思考过程（Qwen 等模型会输出分析过程）
                # 查找真正的 Markdown 内容开始位置
                lines = formatted_content.split('\n')
                content_start = 0
                for i, line in enumerate(lines):
                    # 跳过思考性文字，找到真正的标题或内容
                    if line.startswith('# ') or line.startswith('## ') or line.startswith('### '):
                        content_start = i
                        break
                    # 跳过明显的思考行
                    if any(keyword in line for keyword in ['首先', '然后', '接下来', '最后', '比如', '比如：', '需要注意', '检查后发现', '现在开始']):
                        continue
                    # 找到实质性内容的开始
                    if line.strip() and not any(keyword in line for keyword in ['用户现在', '首先看', '首先处理', '然后看', '这部分要']):
                        content_start = i
                        break

                formatted_content = '\n'.join(lines[content_start:]).strip()

                # 修复 LaTeX 公式中的转义问题
                formatted_content = fix_latex_escapes(formatted_content)

                print(f"\n✅ 格式化成功！")
                print(f"   耗时: {elapsed_time:.1f}秒")
                print(f"   Prompt tokens: {result.get('usage', {}).get('prompt_tokens', 'N/A')}")
                print(f"   Completion tokens: {result.get('usage', {}).get('completion_tokens', 'N/A')}")
                print(f"\n   格式化内容预览（前200字符）：")
                print(formatted_content[:200])
                return formatted_content
            else:
                print(f"\n❌ 格式化失败：未返回内容")
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
    import argparse

    parser = argparse.ArgumentParser(description="使用本地 LLM 格式化 Markdown 文档")
    parser.add_argument("md_file", help="GLM-4.6V输出的Markdown文件路径")
    parser.add_argument("--model", default="Qwen/Qwen2.5-72B-Instruct",
                       help="模型名称（默认: Qwen/Qwen2.5-72B-Instruct）")
    parser.add_argument("--api-url", default="http://192.168.100.110:9999",
                       help="本地 LLM API 地址（默认: http://192.168.100.110:9999）")

    args = parser.parse_args()

    if not Path(args.md_file).exists():
        print(f"\n❌ 错误：Markdown文件不存在: {args.md_file}")
        sys.exit(1)

    # 格式化
    formatted_content = format_markdown_with_local_llm(
        args.md_file,
        api_url=args.api_url,
        model=args.model
    )

    if formatted_content:
        # 保存格式化后的文件
        md_path = Path(args.md_file)
        output_file = str(md_path.parent / f"{md_path.stem}_formatted.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        print(f"\n✅ 格式化完成！")
        print(f"   📄 输出文件: {output_file}")
        print(f"\n   📊 原始文件: {args.md_file}")
        print(f"\n   💡 提示：可以使用Typora等工具查看格式化效果")
    else:
        print("\n❌ 格式化失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
