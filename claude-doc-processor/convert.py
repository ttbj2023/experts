#!/usr/bin/env python3
"""
统一文档转换器 - v4架构

Claude Doc Processor v4.0
核心设计：DOCX只是PDF的前体，PDF→MD是通用流程

统一流程架构：
  Stage 0: DOCX→PDF预处理（可选）
  Stage 1: PDF类型检测（文档型 vs 扫描型）
  Stage 2: 图片提取（分支选择）
  Stage 3: OCR识别（GLM逐页）
  Stage 3.5: 内容整理（DeepSeek逐页，可选）⭐
  Stage 4: 图片描述（GLM）
  Stage 5: 语义匹配（DeepSeek全局）
  Stage 6: 智能替换（去重+清理）

使用方法:
    ./convert.py document.pdf
    ./convert.py document.docx -o output_dir
    ./convert.py document.pdf --refine-content
    ./convert.py docs/*.pdf --batch
"""

import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli.unified_cmd import main

if __name__ == '__main__':
    main()
