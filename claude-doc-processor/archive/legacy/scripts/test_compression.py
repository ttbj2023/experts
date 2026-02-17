#!/usr/bin/env python3
"""测试不同压缩参数的效果"""

import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor/scripts')

from process_pdf_with_glm46v_v2 import GLM46VProcessor
import json

processor = GLM46VProcessor(api_url="http://192.168.100.110:9999")
image_path = "./output_test_enhanced/正文26春初中非常课课通数学8年级人教_20260215_091710/images/page_001.png"

# 简化提示词
prompt = "请直接识别这个数学教材页面，用Markdown格式输出。表格用Markdown表格格式，数学公式用LaTeX格式($...$或$$...$$)。不要输出思考过程，直接输出识别结果。"

test_params = [
    (768, 75, "推荐参数"),
    (1024, 70, "中等尺寸"),
    (512, 80, "小尺寸高质量"),
]

for max_size, quality, desc in test_params:
    print(f"\n{'='*60}")
    print(f"测试: {desc} (max_size={max_size}, quality={quality})")
    print('='*60)

    # 压缩图片
    image_base64 = processor.compress_image(image_path, max_size=max_size, quality=quality)

    # 调用API
    response = processor.call_glm46v_api(image_base64, prompt, max_tokens=65536, retry_count=0)

    # 统计
    if "error" not in response:
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        content = response["choices"][0]["message"]["content"]
        finish_reason = response["choices"][0].get("finish_reason", "unknown")

        print(f"✅ Token使用:")
        print(f"   - 输入(图片): {prompt_tokens}")
        print(f"   - 输出: {completion_tokens}")
        print(f"   - 总计: {total_tokens}")
        print(f"   - 完成原因: {finish_reason}")
        print(f"✅ 输出长度: {len(content)} 字符")
        print(f"✅ 内容预览: {content[:200]}...")
    else:
        print(f"❌ 错误: {response['error']}")
