#!/usr/bin/env python3
"""
修复Markdown表格的分隔行问题
自动检测并修复缺少分隔行的表格
"""

import re
import sys
from pathlib import Path


def fix_markdown_tables(content: str) -> str:
    """
    修复Markdown表格，添加缺失的分隔行
    
    规则：
    1. 检测连续的表格行（以 | 开头）
    2. 如果第一行和第二行之间没有分隔行（|---|），则插入
    3. 如果有超过2行的连续表格行，确保只有第一组是表头+分隔+数据
    
    Args:
        content: Markdown内容
        
    Returns:
        修复后的内容
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 检测是否是表格行（以 | 开头和结尾）
        if line.startswith('|') and line.endswith('|'):
            # 收集连续的表格行
            table_lines = [line]
            j = i + 1
            
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('|') and next_line.endswith('|'):
                    table_lines.append(next_line)
                    j += 1
                else:
                    break
            
            # 分析表格结构
            if len(table_lines) >= 2:
                # 检查第二行是否是分隔行
                second_line = table_lines[1].strip()
                is_separator = all(
                    cell.strip().startswith('-') or cell.strip() == ''
                    for cell in re.split(r'\|', second_line[1:-1])
                )
                
                if not is_separator:
                    # 第二行不是分隔行，插入分隔行
                    # 从第一行生成列数
                    first_line = table_lines[0]
                    # 计算列数（减去首尾的 |）
                    cells = [c.strip() for c in re.split(r'\|', first_line[1:-1])]
                    col_count = len(cells)
                    
                    # 生成分隔行
                    separator = '|' + '|'.join(['---'] * col_count) + '|'
                    
                    # 插入分隔行
                    result.append(table_lines[0])  # 表头
                    result.append(separator)       # 分隔行
                    result.extend(table_lines[1:])  # 数据行
                else:
                    # 已有分隔行，直接添加
                    result.extend(table_lines)
                
                i = j
            else:
                # 只有一行，不是有效表格
                result.append(line)
                i += 1
        else:
            result.append(lines[i])
            i += 1
    
    return '\n'.join(result)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fix_markdown_tables.py <markdown文件> [输出文件]")
        print("\n示例:")
        print("  python3 fix_markdown_tables.py input.md")
        print("  python3 fix_markdown_tables.py input.md output.md")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"错误：文件不存在 - {input_file}")
        sys.exit(1)
    
    # 读取文件
    print(f"📖 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复表格
    print("🔧 修复表格中...")
    fixed_content = fix_markdown_tables(content)
    
    # 确定输出文件
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.parent / f"{input_file.stem}_fixed{input_file.suffix}"
    
    # 写入文件
    print(f"💾 保存到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    # 统计信息
    original_tables = content.count('\n|')  # 粗略统计
    fixed_tables = fixed_content.count('\n|---')
    
    print(f"\n✅ 修复完成！")
    print(f"   原始文件: {input_file}")
    print(f"   输出文件: {output_file}")
    print(f"   添加分隔行: 约{fixed_tables} 个表格")


if __name__ == '__main__':
    main()
