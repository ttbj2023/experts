#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown清理工具

移除文档开头的元信息（处理时间、模型等）
"""

import os
import re
import sys


def cleanup_markdown(md_path: str, output_path: str = None):
    """
    清理Markdown文件，移除开头的元信息

    Args:
        md_path: 输入Markdown文件路径
        output_path: 输出文件路径（默认覆盖原文件）
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除开头的元信息块
    # 匹配从 # _temp 开始到 --- 结束的内容
    pattern = r'^# _temp\n.*?---\n\n'
    cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)

    # 如果没有匹配到，尝试另一种模式
    if cleaned_content == content:
        pattern = r'^# _temp\n.*?\n\n'
        cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)

    # 确定输出路径
    if output_path is None:
        output_path = md_path

    # 保存清理后的内容
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"✓ 清理完成: {md_path}")
    print(f"  移除字符数: {len(content) - len(cleaned_content)}")
    print(f"  输出文件: {output_path}")

    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python3 cleanup_md.py <md_file> [output_file]")
        print("示例: python3 cleanup_md.py document.md document_cleaned.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        sys.exit(1)

    print("=" * 60)
    print("Markdown 清理工具")
    print("=" * 60)
    print(f"输入文件: {input_file}")
    if output_file:
        print(f"输出文件: {output_file}")
    print("=" * 60)

    cleanup_markdown(input_file, output_file)

    print("\n✅ 处理成功！")


if __name__ == "__main__":
    main()
