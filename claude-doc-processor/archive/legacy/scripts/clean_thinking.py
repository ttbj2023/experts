#!/usr/bin/env python3
"""
清理Markdown文件中的思考过程
"""

import os
import sys
import re
from pathlib import Path


def clean_markdown_file(input_path: str, output_path: str = None):
    """
    清理Markdown文件中的思考过程

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径（None则覆盖原文件）
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    cleaned_lines = []

    # 查找第一个真正内容的开始位置
    content_start_idx = 0

    for idx, line in enumerate(lines):
        # 跳过标题之前的所有内容
        if line.startswith('# '):
            # 确保这是一个文档标题而不是描述
            if not any(keyword in line for keyword in ['用户', '提供', 'PDF', '需要', '识别', '转换', '首先', '然后']):
                content_start_idx = idx
                break

    # 从内容开始位置清理
    in_thinking = True
    for line in lines[content_start_idx:]:
        line_stripped = line.strip()

        # 跳过空行
        if not line_stripped:
            cleaned_lines.append(line)
            continue

        # 判断是否是思考行
        is_thinking = any(pattern in line for pattern in [
            '首先看', '然后处理', '现在需要', '接下来', '注意',
            '需要确保', '应该包含', '不仔细看', '不对', '原题图中',
            '首先', '段：', '然后', '部分：', '接着', '最后'
        ]) and not (
            line_stripped.startswith('#') or
            line_stripped.startswith('|') or
            line_stripped.startswith('```') or
            re.match(r'^\d+\.', line_stripped) or  # 以数字开头，如 "1."
            (line_stripped[0].isdigit() and '(' in line_stripped)  # 如 "(2025"
        )

        if not is_thinking:
            cleaned_lines.append(line)

    cleaned_content = '\n'.join(cleaned_lines)

    # 保存
    output_path = output_path or input_path
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"✓ 已清理: {input_path}")


def clean_directory(directory: str):
    """清理目录下所有Markdown文件"""
    dir_path = Path(directory)

    for md_file in dir_path.glob('*.md'):
        clean_markdown_file(str(md_file))

    print(f"\n✅ 完成！已清理目录: {directory}")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  清理单个文件: python clean_thinking.py <file.md>")
        print("  清理整个目录: python clean_thinking.py <directory>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        clean_markdown_file(input_path)
    elif os.path.isdir(input_path):
        clean_directory(input_path)
    else:
        print(f"❌ 错误: 路径不存在: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
