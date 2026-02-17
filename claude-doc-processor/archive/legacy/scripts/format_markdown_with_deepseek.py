#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown排版优化脚本
使用DeepSeek-Chat对OCR识别的Markdown进行排版优化
"""

import os
import sys
import re
import json
import requests
import logging
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Markdown排版优化器"""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化排版器

        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def format_markdown(
        self,
        input_file: str,
        output_file: str,
        model: str = "deepseek-chat"
    ) -> str:
        """
        格式化Markdown文件

        Args:
            input_file: 输入Markdown文件路径
            output_file: 输出Markdown文件路径
            model: 使用的模型名称

        Returns:
            输出文件路径
        """
        logger.info("\n" + "="*60)
        logger.info("Markdown 排版优化")
        logger.info("="*60)
        logger.info(f"输入文件: {input_file}")
        logger.info(f"输出文件: {output_file}")
        logger.info(f"模型: {model}")
        logger.info(f"模型限制: 上下文128K tokens，最大输出65K tokens")

        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"文件大小: {len(content):,} 字符")
        logger.info("开始排版优化...")

        # 一次性处理整个文件
        formatted_content = self._format_with_deepseek(content, model)

        # 保存输出文件
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        logger.info(f"\n✅ 排版完成！")
        logger.info(f"输出文件: {output_file}")
        logger.info(f"原始字符: {len(content):,}")
        logger.info(f"输出字符: {len(formatted_content):,}")

        return output_file

    def _format_with_deepseek(self, content: str, model: str) -> str:
        """
        使用DeepSeek API格式化文本

        Args:
            content: 待格式化的内容
            model: 模型名称

        Returns:
            格式化后的内容
        """
        # 构建prompt
        prompt = f"""你是一个专业的Markdown排版专家。请对以下Markdown文本进行排版优化。

## 排版要求

### 1. 标题层级规范
- 一级标题：使用 `#` （如：# 一、茶树的起源）
- 二级标题：使用 `##` （如：## (一) 茶树起源的佐证）
- 三级标题：使用 `###` （如：### 1. 最早的茶字）
- 四级标题：使用 `####` （如：#### (1) "茶"字的由来）
- 五级标题：使用 `#####` （如：##### ① 若）

规则：
- 标题序号保留中文数字（一、二、三）和阿拉伯数字（1、2、3）
- 括号标题保留括号（（一）、(1)）
- 列表标记（①②③）前添加 `##### ` 作为五级标题

### 2. 列表格式规范
- 无序列表：使用 `- ` 开头（如：- 第一点）
- 有序列表：使用 `1. ` 开头（如：1. 第一步）
- 嵌套列表：使用缩进（2空格或4空格）
- 将 `①②③④⑤⑥⑦` 等标记转为列表项，格式为：
  ```
  - ① 若
  - ② 槚
  - ③ 莽
  ```

### 3. 页面连接处理
- 移除页面之间的断句（如孤立的"为50～60年。"）
- 保持段落的完整性
- 移除误识别的页码（如单独成行的数字"6"、"123"等）

### 4. 文本清理
- 移除多余空行（保留1个空行分隔段落）
- 移除行首行尾多余空格
- 修复明显的OCR错误（如"茶"应该是"荼"在古籍引用中）

### 5. 格式统一
- 标题与内容之间保留1个空行
- 段落之间保留1个空行
- 列表项之间不保留空行

## 输入文本

```
{content}
```

## 输出要求

1. **只输出优化后的Markdown内容**，不要有解释或前言
2. 保持原意不变，只优化格式
3. 不要删除任何内容
4. 输出必须是纯Markdown格式，不要使用markdown代码块包裹

现在请开始排版优化：
"""

        # 调用API
        try:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  # 低温度保证格式一致性
                "max_tokens": 8192,  # API限制：最大8192
                "stream": False
            }

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=300  # 5分钟超时
            )

            response.raise_for_status()
            result = response.json()

            # 提取格式化后的内容
            formatted_text = result['choices'][0]['message']['content'].strip()

            # 移除可能的markdown代码块包裹
            if formatted_text.startswith('```markdown'):
                formatted_text = formatted_text[13:]
            if formatted_text.startswith('```'):
                formatted_text = formatted_text[3:]
            if formatted_text.endswith('```'):
                formatted_text = formatted_text[:-3]

            formatted_text = formatted_text.strip()

            return formatted_text

        except requests.exceptions.HTTPError as e:
            logger.error(f"API请求失败: {e}")
            logger.error(f"响应状态码: {e.response.status_code}")
            logger.error(f"响应内容: {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise
        except KeyError as e:
            logger.error(f"API响应格式错误: {e}")
            logger.error(f"响应内容: {result}")
            raise


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Markdown排版优化工具')
    parser.add_argument('input_file', help='输入Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出Markdown文件路径（默认：输入文件_formatted.md）')
    parser.add_argument('--api-key', help='DeepSeek API密钥（默认：从环境变量DEEPSEEK_API_KEY读取）')
    parser.add_argument('--base-url', default='https://api.deepseek.com', help='DeepSeek API地址')
    parser.add_argument('--model', default='deepseek-chat', help='模型名称')

    args = parser.parse_args()

    # 获取API密钥
    api_key = args.api_key or os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        logger.error("错误：未提供API密钥")
        logger.error("请通过 --api-key 参数或设置 DEEPSEEK_API_KEY 环境变量")
        sys.exit(1)

    # 确定输出文件
    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(args.input_file)
        output_file = f"{base}_formatted{ext}"

    # 检查输入文件
    if not os.path.exists(args.input_file):
        logger.error(f"错误：输入文件不存在: {args.input_file}")
        sys.exit(1)

    # 创建格式化器并处理
    formatter = MarkdownFormatter(api_key, args.base_url)

    try:
        formatter.format_markdown(
            args.input_file,
            output_file,
            args.model
        )
        logger.info(f"\n🎉 排版优化完成！")
        logger.info(f"输入: {args.input_file}")
        logger.info(f"输出: {output_file}")
    except Exception as e:
        logger.error(f"\n❌ 排版失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
