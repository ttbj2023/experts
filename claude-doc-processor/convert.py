#!/usr/bin/env python3
"""
智能文档转换器 - 统一入口

Claude Doc Processor v2.0
自动识别文档类型并选择最优处理流程

支持格式：
  - PDF: 数字版（快速提取）、扫描版（完整OCR）
  - DOCX: 简单文档（快速提取）、复杂文档（完整处理）

使用方法:
    ./convert.py document.pdf
    ./convert.py document.docx -o output_dir
    ./convert.py docs/*.pdf --batch
"""

import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli.unified_cmd import main

if __name__ == '__main__':
    main()
