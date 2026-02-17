#!/usr/bin/env python3
"""测试API响应，查看原始内容"""

import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor/scripts')

from process_pdf_with_glm46v_v2 import GLM46VProcessor
import json

# 创建处理器
processor = GLM46VProcessor(api_url="http://192.168.100.110:9999")

# 使用第一页的图片
image_path = "./output_test_enhanced/正文26春初中非常课课通数学8年级人教_20260215_091710/images/page_001.png"

print(f"📷 读取图片: {image_path}")
image_base64 = processor.compress_image(image_path, max_size=2048, quality=85)

prompt = """请将这个PDF页面转换为Markdown格式。直接输出内容，不要添加任何解释或思考过程。

格式要求：
1. **标题层级**：使用 # ## ### #### 表示不同级别标题
2. **表格格式**：
   - 必须使用标准Markdown表格语法
   - 表头行和数据行之间必须有分隔行（如 |---|---|）
   - 确保所有列对齐正确
   - 表格中不能有空列
3. **数学公式**：
   - 行内公式使用 $...$ 格式
   - 独立公式行使用 $$...$$ 格式
   - 使用标准LaTeX语法（如 \frac{a}{b}、\sqrt{x}、\sum_{i=1}^{n}）
   - 保持原公式的准确性
4. **其他格式**：
   - 列表使用 - 或 1. 格式
   - 保留原文的缩进和层级关系
   - 代码块用 ```语言 包裹

特别注意：
- 不要输出任何思考过程或解释性文字
- 确保表格格式完全正确（表头、分隔行、数据行完整）
- 数学公式必须使用LaTeX格式，不要用纯文本
- 保留所有关键信息，不要遗漏
"""

print(f"\n🔍 调用API...")
response = processor.call_glm46v_api(image_base64, prompt, max_tokens=65536, retry_count=0)

print(f"\n📋 响应状态码: {response.get('error', '成功')}")

if "error" in response:
    print(f"❌ 错误: {response['error']}")
else:
    print(f"\n✅ API调用成功")
    print(f"   - 模型: {response.get('model', 'N/A')}")
    print(f"   - Tokens: {response.get('usage', {}).get('total_tokens', 'N/A')}")

    content = response["choices"][0]["message"]["content"]

    print(f"\n📄 内容长度: {len(content)} 字符")
    print(f"\n{'='*60}")
    print("原始内容（前2000字符）:")
    print('='*60)
    print(content[:2000])
    print('='*60)
    print(f"\n... (还有 {len(content)-2000} 字符)")

    # 保存完整内容
    with open("./debug_raw_response.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n💾 完整内容已保存到: ./debug_raw_response.txt")
