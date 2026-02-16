#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转 Word 兼容 HTML 转换器
================================

便捷脚本，用于将 Markdown 文件转换为 Word 完全兼容的 HTML 文档。

使用方法：
```bash
./convert-md-to-html.py document.md -o output/
```

功能特性：
- ✅ 解析 Markdown 结构
- ✅ 生成 HTML 4.01 + CSS 2.1 兼容代码
- ✅ Base64 内嵌图片（无裂图）
- ✅ MathJax 公式支持（可编辑）
- ✅ 支持多栏布局、复杂表格、多层列表

输出：
- Word 兼容的 HTML 文件
- 用 Word 打开后可直接另存为 DOCX

作者：Claude Code
版本：v1.0
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.cli.markdown_cmd import main

if __name__ == '__main__':
    main()
