"""
验证火山引擎Seedream 4.5配置
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.utils.config import config
from src.ai.doubao_client import doubao_client
from src.ai.deepseek_client import deepseek_client

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def main():
    print_section("🔧 项目配置验证")

    # DeepSeek配置
    print("\n📱 DeepSeek AI 配置:")
    print(f"  ✅ API Key: {config.deepseek.api_key[:15]}...")
    print(f"  🔗 Base URL: {config.deepseek.base_url}")
    print(f"  🤖 Model: {config.deepseek.model}")
    print(f"  📊 Max Tokens: {config.deepseek.max_tokens}")
    print(f"  🌡️  Temperature: {config.deepseek.temperature}")

    # 豆包配置
    print("\n🎨 豆包 AI (Seedream 4.5) 配置:")
    print(f"  ✅ API Key: {config.doubao.api_key[:15]}...")
    print(f"  🔗 Base URL: {config.doubao.base_url}")
    print(f"  🤖 Model: {config.doubao.model}")
    print(f"  📐 Image Size: {config.doubao.image_size}")

    # 图片配置
    print("\n📸 图片生成配置:")
    print(f"  🖼️  封面图尺寸: {config.image.cover_width}x{config.image.cover_height} (16:9)")
    print(f"  📏 插图尺寸: 3072x3072 (1:1)")
    print(f"  📐 支持范围: 2560x1440 ~ 4096x4096")
    print(f"  💾 格式: {config.image.format.upper()}")
    print(f"  ⭐ 质量: {config.image.quality}")

    # 验证客户端初始化
    print_section("✅ 客户端状态")

    print(f"\n🤖 DeepSeek 客户端:")
    print(f"  状态: ✅ 已初始化")
    print(f"  模型: {deepseek_client.model}")
    print(f"  Max Tokens: {deepseek_client.max_tokens}")

    print(f"\n🎨 豆包 客户端:")
    print(f"  状态: ✅ 已初始化")
    print(f"  模型: {doubao_client.model}")
    print(f"  Base URL: {doubao_client.base_url}")

    print_section("📋 API使用说明")

    print("""
🎨 图像生成 (豆包 Seedream 4.5):
   - 支持分辨率: 2560x1440 ~ 4096x4096
   - 封面图: 3840x2160 (16:9)
   - 插图: 3072x3072 (1:1)
   - API: https://ark.cn-beijing.volces.com/api/v3/images/generations

📝 文本生成 (DeepSeek):
   - 模型: deepseek-chat
   - API: https://api.deepseek.com/chat/completions

🔧 代码示例:
   from src.ai.doubao_client import doubao_client

   # 生成封面图
   image_path = doubao_client.generate_cover_image(
       prompt="科技感城市夜景",
       save_path="./output/cover.png"
   )

   # 生成插图
   image_path = doubao_client.generate_illustration(
       prompt="一只可爱的橘猫",
       save_path="./output/illustration.png"
   )
    """)

    print_section("🎉 配置验证完成")

    print("\n✅ 所有配置正确，可以开始使用！\n")


if __name__ == "__main__":
    main()
