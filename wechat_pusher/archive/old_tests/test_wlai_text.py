"""
测试WLAI供应商的文本生成模型
"""
import requests
import json

WLAI_BASE_URL = "https://api3.wlai.vip"
WLAI_API_KEY = "sk-hkqVZcP8OOYxAJuyTYQqkLIhk6naKicwFQCkXcSm9JlSpigZ"

# 测试常见的文本生成模型
TEXT_MODELS = [
    ("DeepSeek", "deepseek-chat"),
    ("DeepSeek R1", "deepseek-r1"),
    ("GPT-4", "gpt-4o"),
    ("GPT-3.5", "gpt-3.5-turbo"),
    ("Claude", "claude-3-5-sonnet-20241022"),
    ("豆包", "doubao-pro-32k"),
    ("豆包Lite", "doubao-lite-32k"),
]

def test_text_model(model_name, display_name):
    """测试文本生成模型"""
    url = f"{WLAI_BASE_URL}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {WLAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "你好，请用一句话介绍你自己。"
            }
        ],
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return {
                "name": display_name,
                "model": model_name,
                "success": True,
                "response": content[:100]
            }
        else:
            return {
                "name": display_name,
                "model": model_name,
                "success": False,
                "error": f"状态码: {response.status_code}, {response.text[:100]}"
            }

    except Exception as e:
        return {
            "name": display_name,
            "model": model_name,
            "success": False,
            "error": str(e)[:100]
        }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 测试WLAI供应商的文本生成模型")
    print("=" * 60)
    print()

    results = []

    for display_name, model_name in TEXT_MODELS:
        print(f"🧪 测试: {display_name} ({model_name})")
        result = test_text_model(model_name, display_name)
        results.append(result)

        if result['success']:
            print(f"  ✅ 成功！")
            print(f"  回复: {result['response']}")
            break
        else:
            print(f"  ❌ 失败: {result['error']}")

        print()

    print("=" * 60)
    print("📊 总结")
    print("=" * 60)

    successful = [r for r in results if r['success']]
    if successful:
        print(f"\n✅ 可用的模型:")
        for r in successful:
            print(f"  • {r['name']} ({r['model']})")
    else:
        print("\n❌ 没有找到可用的模型")
        print("\n💡 可能的原因:")
        print("  1. API Key权限不足")
        print("  2. 供应商服务暂时不可用")
        print("  3. 模型名称不正确")
