#!/usr/bin/env python3
"""
DOCX转Markdown - 便捷启动脚本

使用方法:
    ./convert-docx.py input.docx -o output_dir
    ./convert-docx.py input.docx --glm-api-key YOUR_KEY
"""

import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli.docx_cmd import main

if __name__ == '__main__':
    main()
