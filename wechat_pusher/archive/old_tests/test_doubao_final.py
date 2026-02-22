"""
测试火山引擎Seedream 4.5图像生成
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.ai.doubao_client import doubao_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_generate_image():
    """测试图像生成"""
    print("=" * 60)
    print("🧪 测试火山引擎 Seedream 4.5 图像生成")
    print("=" * 60)
    print()

    # 测试提示词
    prompt = "一只可爱的橘猫在阳光下睡觉，写实风格，高清，柔和光线"

    print(f"📝 提示词: {prompt}")
    print(f"🎨 模型: {doubao_client.model}")
    print(f"🔗 Base URL: {doubao_client.base_url}")
    print()

    print("⏳ 正在生成图片...")
    print()

    # 生成图片
    result_path = doubao_client.generate_image(
        prompt=prompt,
        save_path="./output/test_cat_image.png"
    )

    if result_path:
        print()
        print("=" * 60)
        print("✅ 成功！")
        print("=" * 60)
        print(f"📁 图片已保存到: {result_path}")
    else:
        print()
        print("=" * 60)
        print("❌ 失败！")
        print("=" * 60)
        print("图片生成失败，请检查日志了解详情")


def test_generate_cover():
    """测试封面图生成"""
    print("\n" + "=" * 60)
    print("🧪 测试封面图生成 (16:9)")
    print("=" * 60)
    print()

    prompt = "科技感城市夜景，霓虹灯光，未来风格"

    print(f"📝 提示词: {prompt}")
    print()

    print("⏳ 正在生成封面图...")
    print()

    result_path = doubao_client.generate_cover_image(
        prompt=prompt,
        save_path="./output/test_cover_image.png"
    )

    if result_path:
        print()
        print("=" * 60)
        print("✅ 成功！")
        print("=" * 60)
        print(f"📁 封面图已保存到: {result_path}")
    else:
        print()
        print("=" * 60)
        print("❌ 失败！")
        print("=" * 60)
        print("封面图生成失败，请检查日志了解详情")


if __name__ == "__main__":
    # 测试1: 标准图片生成
    test_generate_image()

    # 测试2: 封面图生成
    # test_generate_cover()

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
