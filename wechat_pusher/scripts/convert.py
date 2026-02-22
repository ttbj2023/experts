#!/usr/bin/env python3
"""
微信公众号 Markdown 转换器 CLI

使用方法：
    python scripts/convert.py input.md [output.html]
    
示例：
    python scripts/convert.py article.md
    python scripts/convert.py article.md output/article.html
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.converter.wechat_markdown_converter import convert_markdown_to_wechat


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 执行转换
    convert_markdown_to_wechat(markdown_file, output_file)


if __name__ == "__main__":
    main()
