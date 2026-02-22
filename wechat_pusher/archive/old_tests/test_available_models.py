"""
测试WLAI供应商可能支持的其他图像生成模型
"""
import requests
import json
import time

WLAI_BASE_URL = "https://api3.wlai.vip"
WLAI_API_KEY = "sk-hkqVZcP8OOYxAJuyTYQqkLIhk6naKicwFQCkXcSm9JlSpigZ"

# 常见的图像生成模型
IMAGE_MODELS = [
    # OpenAI
    ("DALL-E 3", "dall-e-3"),
    ("DALL-E 2", "dall-e-2"),

    # 豆包系列
    ("豆包3.0", "doubao-seedream-3-0-t2i-250415"),
    ("豆包4.0", "doubao-seedream-4-0-250828"),
    ("豆包4.5", "doubao-seedream-4-5-251128"),
    ("豆包5.0", "doubao-seedream-5-0-260128"),

    # Stable Diffusion
    ("SDXL", "stable-diffusion-xl"),
    ("SD 1.5", "stable-diffusion-1.5"),

    # Midjourney
    ("Midjourney", "midjourney"),

    # 其他
    ("Flux", "flux-pro"),
    ("Flux Dev", "flux-dev"),
]

PROMPT = "一只可爱的橘猫在阳光下睡觉，写实风格，高清"

def test_image_model(model_name, display_name):
    """测试图像生成模型"""
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

        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0].get('url', 'N/A')
                return {
                    "name": display_name,
                    "model": model_name,
                    "success": True,
                    "url": image_url
                }

        return {
            "name": display_name,
            "model": model_name,
            "success": False,
            "status": response.status_code,
            "error": response.text[:150] if response.status_code != 200 else "Unknown error"
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
    print("🔍 测试WLAI供应商的图像生成模型")
    print("=" * 60)
    print()

    results = []
    success_count = 0

    for display_name, model_name in IMAGE_MODELS:
        print(f"🧪 测试: {display_name} ({model_name})")
        result = test_image_model(model_name, display_name)
        results.append(result)

        if result['success']:
            print(f"  ✅ 成功！")
            print(f"  🔗 图片URL: {result['url'][:80]}...")
            success_count += 1
            break  # 找到一个可用的就停止
        else:
            status = result.get('status', 'N/A')
            error = result.get('error', '')[:100]
            print(f"  ❌ 失败 (状态码: {status})")
            if status not in [429, 503]:  # 只显示非负载错误的详情
                print(f"     {error}")

        print()
        time.sleep(0.3)  # 避免请求过快

    print("=" * 60)
    print("📊 总结")
    print("=" * 60)

    if success_count > 0:
        print(f"\n✅ 找到 {success_count} 个可用的模型:")
        for r in results:
            if r['success']:
                print(f"  • {r['name']} ({r['model']})")
    else:
        print("\n❌ 没有找到可用的图像生成模型")
        print("\n💡 建议使用火山引擎官方API:")
        print("  URL: https://ark.cn-beijing.volces.com/api/v3/images/generations")
        print("  模型: doubao-seedream-4-5-251128")
        print("  API Key: 4a94a84d-4660-4aa2-95a6-0a344e9ec862")
