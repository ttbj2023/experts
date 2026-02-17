#!/usr/bin/env python3
"""
简化的后处理函数
- 删除 <|beginofthink|> 标签（保留内容）
- 删除 <|endofthink|> 标签（保留内容）
- 删除 <|beginofbox|> 标签（保留内容）
- 删除 <|endofbox|> 标签（保留内容）
"""

import re


def post_process_content(content: str) -> str:
    """
    简化的后处理：只删除特殊标签，保留内容

    Args:
        content: 原始识别内容

    Returns:
        处理后的内容
    """
    # 1. 删除 think 标签（保留内容）
    content = re.sub(r'<\|beginofthink\|>', '', content)
    content = re.sub(r'<\|endofthink\|>', '', content)

    # 2. 删除 box 标签（保留内容）
    content = re.sub(r'<\|beginofbox\|>', '', content)
    content = re.sub(r'<\|endofbox\|>', '', content)

    # 3. 清理首尾空白
    content = content.strip()

    return content


if __name__ == "__main__":
    # 测试
    test_content = """
<|beginofthink|>
这是思考过程
<|endofthink|>

<|beginofbox|>
这是实际内容
<|endofbox|>
    """

    result = post_process_content(test_content)
    print("处理结果:")
    print(result)
