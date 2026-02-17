#!/usr/bin/env python3
"""
监控LM Studio模型切换
每2秒检测一次，直到模型切换成功
"""

import json
import requests
import time

API_URL = "http://192.168.100.110:9999"
TARGET_MODEL = "gpt-oss:20b"  # 你想切换到的模型

headers = {"Content-Type": "application/json"}

print(f"🔍 监控LM Studio模型切换")
print(f"   目标模型: {TARGET_MODEL}")
print(f"   API地址: {API_URL}")
print(f"\n💡 请在LM Studio中切换到: {TARGET_MODEL}")
print(f"⏳ 每秒检测一次...\n")

check_count = 0
while True:
    check_count += 1

    payload = {
        "model": TARGET_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "请只回答：当前模型名称"
            }
        ],
        "stream": False,
        "max_tokens": 50
    }

    try:
        response = requests.post(f"{API_URL}/v1/chat/completions",
                               headers=headers, json=payload, timeout=5)

        if response.status_code == 200:
            result = response.json()
            actual_model = result.get('model', 'unknown')

            # 获取回答
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content'].strip()

            print(f"[{check_count:03d}] 模型: {actual_model:40s} | 回答: {answer}")

            # 检查是否切换成功
            if TARGET_MODEL in actual_model:
                print(f"\n✅ 模型切换成功！")
                print(f"   当前模型: {actual_model}")
                print(f"\n🎉 现在可以运行格式化脚本了！")
                break
            else:
                print(" → ⏳ 等待切换...")
        else:
            print(f"[{check_count:03d}] ❌ API错误: {response.status_code}")

    except Exception as e:
        print(f"[{check_count:03d}] ⚠️  连接失败: {str(e)[:50]}")

    time.sleep(2)  # 等待2秒后再次检测

    if check_count >= 150:  # 最多等待5分钟
        print(f"\n⏰ 等待超时（5分钟）")
        print(f"💡 请检查：")
        print(f"   1. 模型'{TARGET_MODEL}'是否在LM Studio的模型列表中")
        print(f"   2. 是否已成功加载")
        print(f"   3. LM Studio是否正常运行")
        break
