"""
测试 api3.wlai.vip 供应商的OpenAI格式API
"""
import requests
import json
import time

# 供应商配置
WLAI_BASE_URL = "https://api3.wlai.vip"
WLAI_API_KEY = "sk-hkqVZcP8OOYxAJuyTYQqkLIhk6naKicwFQCkXcSm9JlSpigZ"  # WLAI供应商的API Key
MODEL = "doubao-seedream-4-5-251128"

def test_wlai_image_generation():
    """测试wlai图像生成API"""
    print("=" * 60)
    print("测试: WLAI 图像生成 (doubao-seedream-4-5)")
    print("=" * 60)

    url = f"{WLAI_BASE_URL}/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {WLAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "prompt": "一只可爱的橘猫在阳光下睡觉，写实风格，高清，柔和光线",
        "n": 1,
        "size": "1024x1024"
    }

    try:
        print(f"\n📤 发送请求到: {url}")
        print(f"🎨 模型: {MODEL}")
        print(f"🔑 API Key: {WLAI_API_KEY[:20]}...")
        print(f"📝 提示词: 一只可爱的橘猫在阳光下睡觉")

        start_time = time.time()

        response = requests.post(url, headers=headers, json=data, timeout=60)

        elapsed_time = time.time() - start_time

        print(f"\n📥 响应状态码: {response.status_code}")
        print(f"⏱️  响应时间: {elapsed_time:.2f}秒")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 成功！响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 提取图片信息
            if 'data' in result and len(result['data']) > 0:
                image_info = result['data'][0]

                if 'url' in image_info:
                    print(f"\n🔗 图片URL:")
                    print(f"  {image_info['url']}")

                if 'b64_json' in image_info:
                    print(f"\n📦 Base64编码图片 (长度: {len(image_info['b64_json'])} 字符)")

            # 打印使用量信息
            if 'usage' in result:
                usage = result['usage']
                print(f"\n📊 使用量:")
                print(json.dumps(usage, indent=2, ensure_ascii=False))

            return True

        else:
            print(f"\n❌ 失败！错误信息:")
            print(response.text)

            # 尝试解析错误
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"\n错误详情:")
                    print(f"  类型: {error_data['error'].get('type', 'Unknown')}")
                    print(f"  消息: {error_data['error'].get('message', 'Unknown')}")
                    print(f"  代码: {error_data['error'].get('code', 'Unknown')}")
            except:
                pass

            return False

    except requests.exceptions.Timeout:
        print(f"\n⏰ 请求超时 (>60秒)")
        return False

    except Exception as e:
        print(f"\n❌ 异常: {e}")
        return False


def test_wlai_text_generation():
    """测试wlai文本生成API（可选）"""
    print("\n" + "=" * 60)
    print("额外测试: WLAI 文本生成 (doubao-1-5-pro)")
    print("=" * 60)

    url = f"{WLAI_BASE_URL}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {WLAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "doubao-1-5-pro-32k-250115",
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
        print(f"🤖 模型: doubao-1-5-pro-32k")

        response = requests.post(url, headers=headers, json=data, timeout=30)

        print(f"\n📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"\n✅ 成功！回复:")
            print(f"  {content}")

            if 'usage' in result:
                usage = result['usage']
                print(f"\n📊 Token使用:")
                print(f"  输入: {usage.get('prompt_tokens', 0)}")
                print(f"  输出: {usage.get('completion_tokens', 0)}")
                print(f"  总计: {usage.get('total_tokens', 0)}")
        else:
            print(f"\n❌ 失败！")
            print(response.text[:500])

    except Exception as e:
        print(f"\n❌ 异常: {e}")


def compare_with_volcengine():
    """与火山引擎官方API对比"""
    print("\n" + "=" * 60)
    print("对比测试: 火山引擎官方API")
    print("=" * 60)

    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

    headers = {
        "Authorization": f"Bearer {WLAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "doubao-seedream-4-5-251128",
        "prompt": "一只可爱的橘猫在阳光下睡觉，写实风格，高清",
        "n": 1,
        "size": "1024x1024"
    }

    try:
        print(f"\n📤 发送请求到火山引擎官方API...")

        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, timeout=60)
        elapsed_time = time.time() - start_time

        print(f"📥 状态码: {response.status_code}")
        print(f"⏱️  响应时间: {elapsed_time:.2f}秒")

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 成功！")
            if 'data' in result and len(result['data']) > 0:
                print(f"🔗 图片URL: {result['data'][0].get('url', 'N/A')[:80]}...")
        else:
            print(f"\n❌ 失败: {response.text[:200]}")

    except Exception as e:
        print(f"\n❌ 异常: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 WLAI API测试脚本")
    print("=" * 60)
    print()

    # 测试1: WLAI图像生成
    wlai_success = test_wlai_image_generation()

    # 测试2: WLAI文本生成（可选）
    # test_wlai_text_generation()

    # 测试3: 对比火山引擎官方API
    # compare_with_volcengine()

    print("\n" + "=" * 60)
    if wlai_success:
        print("✅ WLAI API测试成功")
    else:
        print("❌ WLAI API测试失败")
    print("=" * 60)
