"""
测试DeepSeek AI增强功能 - 使用Bitcoin文章
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.ai.deepseek_client import deepseek_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def load_article():
    """加载Bitcoin文章"""
    with open('/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher/bitcoin_article_draft.md', 'r', encoding='utf-8') as f:
        return f.read()

def test_summary_generation():
    """测试1: 生成文章摘要"""
    print("=" * 80)
    print("🧪 测试1: 生成文章摘要")
    print("=" * 80)
    print()

    article = load_article()
    title = "当算力有了更好的去处：比特币的物理防线正在解体"

    print(f"📝 文章标题: {title}")
    print(f"📄 文章字数: {len(article)} 字")
    print()
    print("⏳ 正在生成摘要...")

    try:
        summary = deepseek_client.generate_summary(article, max_length=200)

        print()
        print("✅ 摘要生成成功！")
        print()
        print("📄 摘要内容:")
        print(f"   {summary}")
        print()

        return summary

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_image_prompts():
    """测试2: 生成配图提示词"""
    print("\n" + "=" * 80)
    print("🧪 测试2: 生成配图提示词")
    print("=" * 80)
    print()

    article = load_article()
    title = "当算力有了更好的去处：比特币的物理防线正在解体"

    print(f"📝 文章标题: {title}")
    print(f"📄 文章字数: {len(article)} 字")
    print()
    print("⏳ 正在生成配图提示词...")

    try:
        prompts = deepseek_client.generate_image_prompts(article, title)

        print()
        print("✅ 配图提示词生成成功！")
        print()

        print("🎨 封面图提示词 (2个选项):")
        for i, prompt in enumerate(prompts.get("cover_prompts", [])[:2], 1):
            print(f"\n   选项{i}:")
            print(f"   {prompt}")

        print("\n" + "-" * 80)
        print("\n🖼️  插图提示词 (3个场景):")
        for i, prompt in enumerate(prompts.get("image_prompts", [])[:3], 1):
            print(f"\n   场景{i}:")
            print(f"   {prompt}")

        if prompts.get("style"):
            print("\n" + "-" * 80)
            print(f"\n🎭 整体风格: {prompts['style']}")

        if prompts.get("color_scheme"):
            print(f"🎨 色彩方案: {prompts['color_scheme']}")

        print()
        return prompts

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_chart_generation():
    """测试3: 生成图表提示词"""
    print("\n" + "=" * 80)
    print("🧪 测试3: 分析是否需要生成图表")
    print("=" * 80)
    print()

    article = load_article()

    print(f"📄 文章字数: {len(article)} 字")
    print()
    print("⏳ 正在分析...")

    try:
        chart_config = deepseek_client.generate_chart_prompt(article)

        print()
        if chart_config:
            print("✅ 检测到数据内容，建议生成图表！")
            print()
            print(f"📊 图表类型: {chart_config['chart_type']}")
            print(f"📈 图表标题: {chart_config['title']}")
            print(f"📝 图表说明: {chart_config['description']}")
            print()
            print("📊 图表数据:")
            print(f"   标签: {chart_config['data']['labels']}")
            print(f"   数值: {chart_config['data']['values']}")
            print(f"   X轴: {chart_config['data']['xlabel']}")
            print(f"   Y轴: {chart_config['data']['ylabel']}")
        else:
            print("ℹ️  本文为议论性文章，无需生成图表")

        print()
        return chart_config

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_content_refinement():
    """测试4: 优化文章内容"""
    print("\n" + "=" * 80)
    print("🧪 测试4: 优化文章内容（微信公众号适配）")
    print("=" * 80)
    print()

    article = load_article()

    print(f"📝 原始字数: {len(article)} 字")
    print()
    print("⏳ 正在优化内容...")

    try:
        refined = deepseek_client.refine_content(article)

        print()
        print("✅ 内容优化成功！")
        print()

        # 统计信息
        original_lines = len(article.split('\n'))
        refined_lines = len(refined.split('\n'))

        print(f"📊 优化统计:")
        print(f"   原始行数: {original_lines}")
        print(f"   优化后行数: {refined_lines}")
        print(f"   字数变化: {len(article)} → {len(refined)}")
        print()

        # 显示部分优化内容
        print("📄 优化后内容预览 (前800字):")
        print("-" * 80)
        print(refined[:800])
        print("...")
        print("-" * 80)

        # 保存完整优化内容
        output_path = '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher/bitcoin_article_refined.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(refined)

        print()
        print(f"💾 完整优化内容已保存到: {output_path}")
        print()

        return refined

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("\n" + "=" * 80)
    print("🧪 DeepSeek AI 增强功能测试 - Bitcoin文章")
    print("=" * 80)
    print()

    print(f"🤖 模型: {deepseek_client.model}")
    print(f"🌡️  温度: {deepseek_client.temperature}")
    print(f"📊 最大Token: {deepseek_client.max_tokens}")
    print()

    results = []

    # 运行所有测试
    print("🚀 开始完整AI增强流程测试\n")

    results.append(("摘要生成", test_summary_generation()))
    results.append(("配图提示词", test_image_prompts()))
    results.append(("图表分析", test_chart_generation()))
    results.append(("内容优化", test_content_refinement()))

    # 总结
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    print()

    for name, result in results:
        if result is not None:
            status = "✅ 成功"
        else:
            status = "❌ 失败"
        print(f"{status} - {name}")

    total = len(results)
    passed = sum(1 for _, r in results if r is not None)

    print()
    print(f"总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有AI增强功能测试通过！")
        print("\n💡 接下来可以:")
        print("   1. 使用生成的配图提示词调用Doubao生成实际图片")
        print("   2. 使用优化后的内容进行Markdown转HTML转换")
        print("   3. 集成完整的AI增强工作流")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
