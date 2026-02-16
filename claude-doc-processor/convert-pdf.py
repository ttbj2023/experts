#!/usr/bin/env python3
"""
PDF转Markdown - 便捷启动脚本

使用方法:
    ./convert-pdf.py input.pdf -o output_dir
    ./convert-pdf.py input.pdf --max-pages 10
"""

import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli.pdf_cmd import main

if __name__ == '__main__':
    main()
