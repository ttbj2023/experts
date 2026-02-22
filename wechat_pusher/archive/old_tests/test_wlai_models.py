"""
测试WLAI供应商支持的不同模型名称
"""
import requests
import json
import time

WLAI_BASE_URL = "https://api3.wlai.vip"
WLAI_API_KEY = "sk-hkqVZcP8OOYxAJuyTYQqkLIhk6naKicwFQCkXcSm9JlSpigZ"

# 常见的模型名称变体
MODEL_VARIANTS = [
    "doubao-seedream-4-5-251128",
    "doubao-seedream-4.5-251128",
    "doubao-seedream-4-5",
    "doubao-seedream-4.5",
    "doubao-seedream-45-251128",
    "seedream-4-5-251128",
    "seedream-4.5",
    "doubao-see-dream-4-5",
    "volc_doubao-seedream-4-5",
    "doubao-seedream-5-0-260128",
    "doubao-seedream-5.0",
    "doubao-seedream-5-0",
]

PROMPT = "一只可爱的橘猫在阳光下睡觉"

def test_model(model_name):
    """测试单个模型"""
    url = f"{WLAI_BASE_URL}/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {WLAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_name,
        "prompt": PROMPT,
        "n": 1,
        "size": "1024x1024"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        return {
            "model": model_name,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.text[:200] if response.status_code != 200 else "Success"
        }

    except Exception as e:
        return {
            "model": model_name,
            "status_code": 0,
            "success": False,
            "response": str(e)[:200]
        }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 测试WLAI供应商支持的模型名称")
    print("=" * 60)
    print()

    results = []

    for model in MODEL_VARIANTS:
        print(f"🧪 测试模型: {model}")
        result = test_model(model)
        results.append(result)

        if result['success']:
            print(f"  ✅ 成功！")
            break
        else:
            print(f"  ❌ 失败 (状态码: {result['status_code']})")
            print(f"     {result['response'][:100]}")

        time.sleep(0.5)  # 避免请求过快

    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"\n✅ 成功: {len(successful)} 个")
    print(f"❌ 失败: {len(failed)} 个")

    if successful:
        print(f"\n🎉 可用的模型名称:")
        for r in successful:
            print(f"  • {r['model']}")

    if failed:
        print(f"\n❌ 失败的模型:")
        for r in failed[:5]:  # 只显示前5个
            print(f"  • {r['model']} (状态码: {r['status_code']})")
