#!/usr/bin/env python3
"""
测试完整的后处理逻辑
"""

import re


def post_process_content(content: str) -> str:
    """
    完整的后处理逻辑

    Args:
        content: 原始识别内容

    Returns:
        处理后的内容
    """
    # 1. 删除 <thinkcont>...</thinkcont> 标签及其所有内容（包括内容本身）
    # 这个标签内的内容是思考过程，需要完整删除
    content = re.sub(r'<thinkcont>.*?</thinkcont>', '', content, flags=re.DOTALL)

    # 2. 删除其他think标签（只删除标签本身，保留内容）
    content = re.sub(r'<\|beginofthink\|>', '', content)
    content = re.sub(r'<\|endofthink\|>', '', content)
    content = re.sub(r'