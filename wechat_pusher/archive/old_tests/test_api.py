"""
测试火山引擎和DeepSeek API调用
"""
import requests
import json
import base64
from pathlib import Path

# 火山引擎配置
VOLC_API_KEY = "4a94a84d-4660-4aa2-95a6-0a344e9ec862"
VOLC_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
VOLC_IMAGE_MODEL = "doubao-seedream-3-0-t2i-250415"  # 使用3.0测试
VOLC_TEXT_MODEL = "doubao-1-5-pro-32k-250115"

# DeepSeek配置
DEEPSEEK_API_KEY = "sk-62f31b03e22048799beefff7cae0dfc3"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

def test_volc_image_generation():
    """测试火山引擎图像生成API"""
    print("=" * 60)
    print("测试1: 火山引擎图像生成 (doubao-seedream-3-0-t2i)")
    print("=" * 60)

    url = f"{VOLC_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {VOLC_API_KEY}",
        "Content-Type": "application/json"
    }

    # 尝试使用chat completions接口生成图片
    data = {
        "model": VOLC_IMAGE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "生成一张图片：一只可爱的橘猫在阳光下睡觉"
            }
        ],
        "stream": False
    }

    try:
        print(f"\n📤 发送请求到: {url}")
        print(f"🎨 模型: {VOLC_IMAGE_MODEL}")
        print(f"📝 提示词: 一只可爱的橘猫在阳光下睡觉")

        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"\n📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 成功！响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 尝试提取图片信息
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                content = message.get('content', '')
                print(f"\n📸 内容类型: {type(content)}")
                print(f"📄 内容预览: {str(content)[:500]}")

        else:
            print(f"\n❌ 失败！错误信息:")
            print(response.text)

    except Exception as e:
        print(f"\n❌ 异常: {e}")

    print()


def test_volc_text_generation():
    """测试火山引擎文本生成API"""
    print("=" * 60)
    print("测试2: 火山引擎文本生成 (doubao-1-5-pro-32k)")
    print("=" * 60)

    url = f"{VOLC_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {VOLC_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": VOLC_TEXT_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "你好，请用一句话介绍你自己。"
            }
        ],
        "stream": False
    }

    try:
        print(f"\n📤 发送请求到: {url}")
        print(f"🤖 模型: {VOLC_TEXT_MODEL}")

        response = requests.post(url, headers=headers, json=data, timeout=30)

        print(f"\n📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"\n✅ 成功！回复:")
            print(f"  {content}")
        else:
            print(f"\n❌ 失败！错误信息:")
            print(response.text)

    except Exception as e:
        print(f"\n❌ 异常: {e}")

    print()


def test_deepseek_text():
    """测试DeepSeek官方API"""
    print("=" * 60)
    print("测试3: DeepSeek官方API (deepseek-chat)")
    print("=" * 60)

    url = f"{DEEPSEEK_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是DeepSeek，由深度求索开发的AI助手。"
            },
            {
                "role": "user",
                "content": "你好！请简单介绍一下你的能力。"
            }
        ],
        "stream": False,
        "temperature": 0.7
    }

    try:
        print(f"\n📤 发送请求到: {url}")
        print(f"🤖 模型: deepseek-chat")

        response = requests.post(url, headers=headers, json=data, timeout=30)

        print(f"\n📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"\n✅ 成功！回复:")
            print(f"  {content}")

            # 打印token使用情况
            if 'usage' in result:
                usage = result['usage']
                print(f"\n📊 Token使用:")
                print(f"  输入: {usage.get('prompt_tokens', 0)} tokens")
                print(f"  输出: {usage.get('completion_tokens', 0)} tokens")
                print(f"  总计: {usage.get('total_tokens', 0)} tokens")
        else:
            print(f"\n❌ 失败！错误信息:")
            print(response.text)

    except Exception as e:
        print(f"\n❌ 异常: {e}")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 API测试脚本")
    print("=" * 60)
    print()

    # 测试火山引擎图像生成
    test_volc_image_generation()

    # 测试火山引擎文本生成
    test_volc_text_generation()

    # 测试DeepSeek官方API
    test_deepseek_text()

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
