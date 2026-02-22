"""
测试火山引擎图像生成API - 多种方式
"""
import requests
import json
import base64
from pathlib import Path

VOLC_API_KEY = "4a94a84d-4660-4aa2-95a6-0a344e9ec862"
VOLC_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
IMAGE_MODEL = "doubao-seedream-3-0-t2i-250415"

def test_openai_images_format():
    """测试OpenAI格式的images API"""
    print("=" * 60)
    print("测试1: OpenAI Images API格式")
    print("=" * 60)

    # 尝试OpenAI标准的images/generations endpoint
    url = f"{VOLC_BASE_URL}/images/generations"

    headers = {
        "Authorization": f"Bearer {VOLC_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": IMAGE_MODEL,
        "prompt": "一只可爱的橘猫在阳光下睡觉，写实风格，高清",
        "n": 1,
        "size": "1024x1024"
    }

    try:
        print(f"\n📤 发送请求到: {url}")
        print(f"🎨 模型: {IMAGE_MODEL}")
        print(f"📝 提示词: 一只可爱的橘猫在阳光下睡觉")

        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"\n📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 成功！响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        else:
            print(f"\n❌ 失败！错误信息:")
            print(response.text)

    except Exception as e:
        print(f"\n❌ 异常: {e}")

    print()


def test_responses_api():
    """测试火山引擎Responses API（多模态）"""
    print("=" * 60)
    print("测试2: 火山引擎Responses API")
    print("=" * 60)

    url = f"{VOLC_BASE_URL}/responses"

    headers = {
        "Authorization": f"Bearer {VOLC_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": IMAGE_MODEL,
        "input": "生成一张图片：一只可爱的橘猫在阳光下睡觉",
        "response_format": {
            "type": "image_url"
        }
    }

    try:
        print(f"\n📤 发送请求到: {url}")
        print(f"🎨 模型: {IMAGE_MODEL}")

        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"\n📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 成功！响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        else:
            print(f"\n❌ 失败！错误信息:")
            print(response.text)

    except Exception as e:
        print(f"\n❌ 异常: {e}")

    print()


def test_chat_with_vision():
    """测试Chat API + Vision方式（如果支持）"""
    print("=" * 60)
    print("测试3: Chat API + 内容类型指定")
    print("=" * 60)

    url = f"{VOLC_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {VOLC_API_KEY}",
        "Content-Type": "application/json"
    }

    # 尝试指定response_format
    data = {
        "model": IMAGE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "生成一张图片：一只可爱的橘猫在阳光下睡觉"
            }
        ],
        "response_format": {"type": "image_url"}
    }

    try:
        print(f"\n📤 发送请求到: {url}")
        print(f"🎨 模型: {IMAGE_MODEL}")

        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"\n📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 成功！响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        else:
            print(f"\n❌ 失败！错误信息:")
            print(response.text)

    except Exception as e:
        print(f"\n❌ 异常: {e}")

    print()


def test_volcengine_sdk():
    """使用火山引擎Python SDK测试"""
    print("=" * 60)
    print("测试4: 查看是否需要安装火山引擎SDK")
    print("=" * 60)

    try:
        import volcenginesdkarkruntime
        print("\n✅ volcenginesdkarkruntime 已安装")

        # 尝试使用SDK
        from volcenginesdkarkruntime import Ark

        client = Ark(
            base_url=VOLC_BASE_URL,
            api_key=VOLC_API_KEY
        )

        print("\n📤 使用SDK发送请求...")

        # 尝试直接调用（可能会失败，因为chat completions不支持图像模型）
        try:
            response = client.chat.completions.create(
                model=IMAGE_MODEL,
                messages=[{"role": "user", "content": "生成一张图片"}]
            )
            print(f"✅ SDK调用成功: {response}")
        except Exception as e:
            print(f"❌ SDK调用失败: {e}")

    except ImportError:
        print("\n❌ volcenginesdkarkruntime 未安装")
        print("💡 可以尝试安装: pip install volcengine-python-sdk")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 火山引擎图像生成API测试")
    print("=" * 60)
    print()

    # 测试1: OpenAI格式
    test_openai_images_format()

    # 测试2: Responses API
    test_responses_api()

    # 测试3: Chat + response_format
    test_chat_with_vision()

    # 测试4: SDK
    test_volcengine_sdk()

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
