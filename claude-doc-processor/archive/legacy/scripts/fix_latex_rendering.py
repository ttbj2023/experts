#!/usr/bin/env python3
"""
修复LaTeX渲染问题（改进版）
1. 移除\text{}命令（Markdown不支持）
2. 替换LaTeX逻辑符号为中文
3. 修复公式和文本混杂的问题
"""

import re
import sys
from pathlib import Path


def fix_latex_rendering(content: str) -> str:
    """
    修复LaTeX渲染问题（改进版）
    
    Args:
        content: Markdown内容
    
    Returns:
            修复后的内容
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 只处理非代码块内容
        if not line.strip().startswith('```'):
            # 修复1: \text{...} -> 直接文本
            # 匹配任何位置的 \text{xxx}
            line = re.sub(r'\\text\{([^}]+)\}', r'\1', line)
            
            # 修复2: \because -> 因为
            line = line.replace(r'\because', '因为')
            
            # 修复3: \therefore -> 所以
            line = line.replace(r'\therefore', '所以')
            
            # 修复4: \implies -> 推出
            line = line.replace(r'\implies', '推出')
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fix_latex_rendering.py <markdown文件> [输出文件]")
        print("\n示例:")
        print("  python3 fix_latex_rendering.py input.md")
        print("  python3 fix_latex_rendering.py input.md output.md")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"错误：文件不存在 - {input_file}")
        sys.exit(1)
    
    # 读取文件
    print(f"📖 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计原始问题数量
    text_count = content.count(r'\text{')
    because_count = content.count(r'\because')
    therefore_count = content.count(r'\therefore')
    
    print(f"📊 原始统计:")
    print(f"   \\text{{}}: {text_count}处")
    print(f"   \\because: {because_count}处")
    print(f"   \\therefore: {therefore_count}处")
    
    # 修复LaTeX问题
    print("\n🔧 修复LaTeX渲染问题...")
    fixed_content = fix_latex_rendering(content)
    
    # 统计修复后数量
    text_count_fixed = fixed_content.count(r'\text{')
    because_count_fixed = fixed_content.count(r'\because')
    therefore_count_fixed = fixed_content.count(r'\therefore')
    
    print(f"📊 修复后统计:")
    print(f"   \\text{{}}: {text_count_fixed}处 (修复了{text_count - text_count_fixed}处)")
    print(f"   \\because: {because_count_fixed}处 (修复了{because_count - because_count_fixed}处)")
    print(f"   \\therefore: {therefore_count_fixed}处 (修复了{therefore_count - therefore_count_fixed}处)")
    
    # 确定输出文件
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.parent / f"{input_file.stem}_latex_fixed{input_file.suffix}"
    
    # 写入文件
    print(f"\n💾 保存到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"\n✅ 修复完成！")
    print(f"   原始文件: {input_file}")
    print(f"   输出文件: {output_file}")


if __name__ == '__main__':
    main()
