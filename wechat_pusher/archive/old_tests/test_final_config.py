"""
验证更正后的微信公众号图片配置
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.utils.config import config
from src.ai.doubao_client import doubao_client

def main():
    print("=" * 60)
    print("✅ 更正后的配置验证")
    print("=" * 60)
    print()

    # 显示图片配置
    print("📸 图片生成配置（Seedream 4.5）:")
    print(f"  封面图（16:9）: {config.image.cover_width}×{config.image.cover_height}px")
    print(f"  正方形封面: {config.image.cover_square_size}×{config.image.cover_square_size}px")
    print(f"  正文插图（黄金比例）: {config.image.illustration_width}×{config.image.illustration_height}px")
    print(f"  内容引导图: {config.image.guide_image_width}×{config.image.guide_image_height}px")
    print(f"  格式: {config.image.format.upper()}")
    print(f"  质量: {config.image.quality}")
    print()

    # 验证比例
    print("📐 比例验证:")
    cover_ratio = config.image.cover_width / config.image.cover_height
    print(f"  封面图比例: {cover_ratio:.2f}:1 (应为 2.35:1 = 2.35)")

    illu_ratio = config.image.illustration_width / config.image.illustration_height
    print(f"  插图比例: {illu_ratio:.2f}:1 (应为 1.62:1 黄金比例)")

    guide_ratio = config.image.guide_image_width / config.image.guide_image_height
    print(f"  引导图比例: {guide_ratio:.2f}:1 (应为 16:9 = 1.78)")
    print()

    # 验证Seedream 4.5范围
    print("🎯 Seedream 4.5 兼容性检查:")
    min_size = 2560 * 1440  # 最小像素
    max_size = 4096 * 4096  # 最大像素

    configs = [
        ("封面图", config.image.cover_width, config.image.cover_height),
        ("正方形封面", config.image.cover_square_size, config.image.cover_square_size),
        ("正文插图", config.image.illustration_width, config.image.illustration_height),
        ("引导图", config.image.guide_image_width, config.image.guide_image_height),
    ]

    all_valid = True
    for name, w, h in configs:
        pixels = w * h
        if pixels < min_size:
            print(f"  ❌ {name}: {w}×{h} - 太小！({pixels} < {min_size})")
            all_valid = False
        elif pixels > max_size:
            print(f"  ❌ {name}: {w}×{h} - 太大！({pixels} > {max_size})")
            all_valid = False
        else:
            print(f"  ✅ {name}: {w}×{h} - 符合要求")

    print()
    print("=" * 60)
    if all_valid:
        print("✅ 所有配置正确！")
    else:
        print("❌ 部分配置不符合要求")
    print("=" * 60)
    print()

    # 使用示例
    print("💡 使用示例:")
    print("""
# 生成封面图（16:9）
cover = doubao_client.generate_cover_image(
    prompt="科技感城市夜景",
    save_path="./output/cover.png"
)

# 生成正文插图（黄金比例）
illustration = doubao_client.generate_illustration(
    prompt="产品展示图",
    save_path="./output/illustration.png"
)

# 自定义尺寸
custom = doubao_client.generate_image(
    prompt="自定义内容",
    width=3840,
    height=2160,
    save_path="./output/custom.png"
)
    """)


if __name__ == "__main__":
    main()
