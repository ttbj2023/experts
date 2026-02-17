#!/usr/bin/env python3
"""测试完整API响应，不过滤think标签"""

import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor/scripts')

from process_pdf_with_glm46v_v2 import GLM46VProcessor
import json

# 创建处理器
processor = GLM46VProcessor(api_url="http://192.168.100.110:9999")

# 使用第一页的图片
image_path = "./output_test_enhanced/正文26春初中非常课课通数学8年级人教_20260215_091710/images/page_001.png"

print(f"📷 读取图片: {image_path}")
print(f"   文件大小: {468}KB")

image_base64 = processor.compress_image(image_path, max_size=2048, quality=85)
print(f"   压缩后base64长度: {len(image_base64)} 字符")

# 简化提示词，强制要求直接输出
prompt = """这是一个数学教材的PDF页面。请直接识别并输出这个页面的内容。

格式要求：
- 标题用 # ## ###
- 表格用 Markdown 表格格式
- 数学公式用 LaTeX 格式，行内公式用 $...$，独立公式用 $$...$$
- 不要输出任何思考过程或解释，直接输出识别的内容

现在开始输出："""

print(f"\n🔍 调用API...")
print(f"   max_tokens: 65536")

response = processor.call_glm46v_api(image_base64, prompt, max_tokens=65536, retry_count=0)

print(f"\n{'='*60}")
print(f"完整API响应:")
print('='*60)
print(json.dumps(response, ensure_ascii=False, indent=2))
print('='*60)
