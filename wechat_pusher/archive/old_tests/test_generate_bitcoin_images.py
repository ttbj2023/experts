"""
使用Doubao生成Bitcoin文章配图
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.ai.doubao_client import doubao_client
from src.ai.deepseek_client import deepseek_client
from src.utils.logger import get_logger
import os

logger = get_logger(__name__)

def main():
    print("=" * 80)
    print("🎨 使用Doubao生成Bitcoin文章配图")
    print("=" * 80)
    print()

    # 加载文章
    with open('/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher/bitcoin_article_draft.md', 'r', encoding='utf-8') as f:
        article = f.read()

    title = "当算力有了更好的去处：比特币的物理防线正在解体"

    # 创建输出目录
    output_dir = '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher/output/bitcoin_article_images'
    os.makedirs(output_dir, exist_ok=True)

    print(f"📂 输出目录: {output_dir}")
    print()

    # 1. 使用DeepSeek生成配图提示词
    print("🧠 步骤1: 使用DeepSeek生成配图提示词...")
    prompts = deepseek_client.generate_image_prompts(article, title)
    print(f"✅ 生成了 {len(prompts['cover_prompts'])} 个封面提示和 {len(prompts['image_prompts'])} 个插图提示")
    print()

    # 2. 生成封面图
    print("=" * 80)
    print("🎨 步骤2: 生成封面图（16:9，3840×1632）")
    print("=" * 80)
    print()

    cover_prompt = prompts['cover_prompts'][0]
    print(f"📝 提示词: {cover_prompt[:100]}...")
    print()

    cover_path = os.path.join(output_dir, 'cover_1.png')
    try:
        result = doubao_client.generate_cover_image(
            prompt=cover_prompt,
            save_path=cover_path
        )

        if result:
            print(f"✅ 封面图生成成功！")
            print(f"   保存路径: {result}")

            # 显示文件大小
            file_size = os.path.getsize(result) / (1024 * 1024)
            print(f"   文件大小: {file_size:.2f} MB")
        else:
            print("❌ 封面图生成失败")

    except Exception as e:
        print(f"❌ 封面图生成异常: {e}")
        import traceback
        traceback.print_exc()

    print()

    # 3. 生成第2个封面图选项
    print("=" * 80)
    print("🎨 步骤3: 生成封面图选项2（16:9，3840×1632）")
    print("=" * 80)
    print()

    if len(prompts['cover_prompts']) > 1:
        cover_prompt_2 = prompts['cover_prompts'][1]
        print(f"📝 提示词: {cover_prompt_2[:100]}...")
        print()

        cover_path_2 = os.path.join(output_dir, 'cover_2.png')
        try:
            result = doubao_client.generate_cover_image(
                prompt=cover_prompt_2,
                save_path=cover_path_2
            )

            if result:
                print(f"✅ 封面图2生成成功！")
                print(f"   保存路径: {result}")

                file_size = os.path.getsize(result) / (1024 * 1024)
                print(f"   文件大小: {file_size:.2f} MB")
            else:
                print("❌ 封面图2生成失败")

        except Exception as e:
            print(f"❌ 封面图2生成异常: {e}")
    else:
        print("ℹ️  只有1个封面提示词")

    print()

    # 4. 生成插图
    print("=" * 80)
    print("🖼️  步骤4: 生成插图（黄金比例，3072×1898）")
    print("=" * 80)
    print()

    illustration_count = min(3, len(prompts['image_prompts']))  # 最多生成3张插图
    generated_illustrations = []

    for i in range(illustration_count):
        prompt = prompts['image_prompts'][i]
        print(f"📝 插图{i+1}提示词: {prompt[:80]}...")
        print()

        illu_path = os.path.join(output_dir, f'illustration_{i+1}.png')

        try:
            result = doubao_client.generate_illustration(
                prompt=prompt,
                save_path=illu_path
            )

            if result:
                print(f"✅ 插图{i+1}生成成功！")
                print(f"   保存路径: {result}")

                file_size = os.path.getsize(result) / (1024 * 1024)
                print(f"   文件大小: {file_size:.2f} MB")

                generated_illustrations.append(result)
            else:
                print(f"❌ 插图{i+1}生成失败")

        except Exception as e:
            print(f"❌ 插图{i+1}生成异常: {e}")
            import traceback
            traceback.print_exc()

        print()

    # 总结
    print("=" * 80)
    print("📊 图片生成总结")
    print("=" * 80)
    print()

    total_generated = (
        (1 if os.path.exists(cover_path) else 0) +
        (1 if os.path.exists(cover_path_2) else 0) +
        len(generated_illustrations)
    )

    print(f"✅ 成功生成: {total_generated} 张图片")
    print(f"📁 保存位置: {output_dir}")
    print()

    print("生成的文件列表:")
    for filename in sorted(os.listdir(output_dir)):
        filepath = os.path.join(output_dir, filename)
        if os.path.isfile(filepath):
            file_size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  📄 {filename} ({file_size:.2f} MB)")

    print()
    print("💡 使用建议:")
    print("   1. 从2个封面图中选择最适合的一张")
    print("   2. 将图片上传到微信公众号素材库")
    print("   3. 在文章编辑器中插入图片")
    print("   4. 微信会自动压缩到显示尺寸（约900px宽）")


if __name__ == "__main__":
    main()
