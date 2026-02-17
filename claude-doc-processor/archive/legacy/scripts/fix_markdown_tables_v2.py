#!/usr/bin/env python3
"""
修复Markdown文件中的表格格式（增强版）
1. 在列表项后的表格前添加空行
2. 为缺少分隔行的表格添加分隔行
3. 删除重复的分隔行
"""

import re
import sys
from pathlib import Path


def fix_markdown_tables(file_path: str) -> None:
    """修复Markdown文件中的表格格式"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 在列表项后的表格前添加空行
    content = re.sub(r'([：:。，,\.]\s*)\n(\|[^|]+\|)', r'\1\n\n\2', content)

    # 2. 按行处理，添加缺失的分隔行
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # 检查是否是表格行（非分隔行）
        if line.strip().startswith('|') and '---' not in line and line.count('|') >= 2:
            # 检查下一行是否也是表格行（非分隔行）
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('|') and '---' not in next_line:
                    # 需要插入分隔行
                    col_count = line.count('|') - 1
                    separator = '|' + '|'.join(['---'] * col_count) + '|'
                    fixed_lines.append(separator)

    # 3. 删除重复的分隔行
    result = []
    prev_was_separator = False

    for line in fixed_lines:
        is_separator = '---' in line and line.strip().startswith('|')

        # 如果当前行是分隔行，且上一行也是分隔行，跳过
        if is_separator and prev_was_separator:
            continue

        result.append(line)
        prev_was_separator = is_separator

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))


def main():
    if len(sys.argv) < 2:
        print("用法: python fix_markdown_tables_v2.py <file_or_dir>")
        sys.exit(1)

    target = sys.argv[1]
    path = Path(target)

    if path.is_file():
        print(f"处理文件: {target}")
        fix_markdown_tables(target)
        print("✓ 完成")
    elif path.is_dir():
        count = 0
        for md_file in path.rglob('*.md'):
            print(f"处理: {md_file}")
            fix_markdown_tables(str(md_file))
            count += 1
        print(f"✓ 完成，共处理 {count} 个文件")
    else:
        print(f"错误: 路径不存在: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
