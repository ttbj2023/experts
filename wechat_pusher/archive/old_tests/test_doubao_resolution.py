"""
测试火山引擎Seedream 4.5图像生成 - 使用正确的分辨率
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.ai.doubao_client import doubao_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_generate_image():
    """测试图像生成 - 使用支持的分辨率"""
    print("=" * 60)
    print("🧪 测试火山引擎 Seedream 4.5 图像生成")
    print("=" * 60)
    print()

    # 测试提示词
    prompt = "一只可爱的橘猫在阳光下睡觉，写实风格，高清，柔和光线"

    # Seedream 4.5 支持的分辨率范围: 2560x1440 到 4096x4096
    # 测试几种常见分辨率
    test_sizes = [
        ("2K (2560x1440)", 2560, 1440),
        ("Square 3K (3072x3072)", 3072, 3072),
        ("4K (3840x2160)", 3840, 2160),
    ]

    for size_name, width, height in test_sizes:
        print(f"\n{'='*60}")
        print(f"📐 测试分辨率: {size_name} ({width}x{height})")
        print(f"{'='*60}")

        print(f"📝 提示词: {prompt}")
        print(f"🎨 模型: {doubao_client.model}")
        print()

        print("⏳ 正在生成图片...")

        # 生成图片
        result_path = doubao_client.generate_image(
            prompt=prompt,
            save_path=f"./output/test_cat_{width}x{height}.png",
            width=width,
            height=height
        )

        if result_path:
            print()
            print("✅ 成功！")
            print(f"📁 图片已保存到: {result_path}")
            break  # 成功就停止测试
        else:
            print()
            print("❌ 失败！")

    print()
    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


def test_generate_cover():
    """测试封面图生成 - 16:9比例"""
    print("\n" + "=" * 60)
    print("🧪 测试封面图生成 (16:9)")
    print("=" * 60)
    print()

    prompt = "科技感城市夜景，霓虹灯光，未来风格"

    # 16:9比例，在2560x1440到4096x4096范围内
    width = 3840
    height = 2160  # 16:9

    print(f"📝 提示词: {prompt}")
    print(f"📐 分辨率: {width}x{height} (16:9)")
    print()

    print("⏳ 正在生成封面图...")

    result_path = doubao_client.generate_image(
        prompt=prompt,
        save_path="./output/test_cover_3840x2160.png",
        width=width,
        height=height
    )

    if result_path:
        print()
        print("✅ 成功！")
        print(f"📁 封面图已保存到: {result_path}")
    else:
        print()
        print("❌ 失败！")


if __name__ == "__main__":
    # 测试1: 标准图片生成（多种分辨率）
    test_generate_image()

    # 测试2: 封面图生成
    # test_generate_cover()
