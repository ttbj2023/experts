#!/usr/bin/env python3
"""
测试本地LLM连接
"""

import json
import requests

API_URL = "http://192.168.100.110:9999"
MODEL_NAME = "gpt-oss:20b"  # 修改为你要测试的模型

headers = {"Content-Type": "application/json"}

payload = {
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "user",
            "content": "请回答：1+1等于几？只回答数字。"
        }
    ],
    "stream": False,
    "max_tokens": 100
}

print(f"🔍 测试本地LLM连接")
print(f"   API地址: {API_URL}")
print(f"   模型名称: {MODEL_NAME}")
print(f"\n📤 发送请求...")
print(f"\n请求内容：")
print(json.dumps(payload, indent=2, ensure_ascii=False))

try:
    response = requests.post(f"{API_URL}/v1/chat/completions",
                           headers=headers, json=payload, timeout=30)

    print(f"\n📥 响应状态: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 成功！")
        print(f"   模型: {result.get('model', 'N/A')}")
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print(f"   回答: {content}")
            print(f"\n   Tokens使用: {result.get('usage', {})}")
    else:
        print(f"\n❌ 失败")
        print(f"   错误信息: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ 连接错误: {e}")
    print(f"\n💡 请检查：")
    print(f"   1. LM Studio是否正在运行")
    print(f"   2. 模型'{MODEL_NAME}'是否已加载")
    print(f"   3. API地址是否正确: {API_URL}")
