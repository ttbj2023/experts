"""
测试DeepSeek客户端功能
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.ai.deepseek_client import deepseek_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_generate_summary():
    """测试1: 生成文章摘要"""
    print("=" * 60)
    print("🧪 测试1: 生成文章摘要")
    print("=" * 60)
    print()

    # 测试文章
    article = """
# Python编程入门指南

Python是一种广泛使用的高级编程语言，由Guido van Rossum于1991年首次发布。
Python具有简洁易读的语法，强制使用空白缩进，让代码具有良好的可读性。

Python的应用领域非常广泛，包括Web开发、数据分析、人工智能、科学计算、自动化运维等。
在人工智能领域，Python是最受欢迎的语言，拥有TensorFlow、PyTorch、scikit-learn等强大的库。

Python的设计哲学强调代码的可读性和简洁的语法，尤其是使用空格缩进划分代码块，
而非使用大括号。相比C++或Java，Python让开发者能够用更少的代码表达概念。

总的来说，Python是一个适合初学者和专业开发者的强大编程语言。
"""

    print(f"📝 原文章字数: {len(article)} 字")
    print()
    print("⏳ 正在生成摘要...")

    try:
        summary = deepseek_client.generate_summary(article, max_length=150)

        print()
        print("✅ 摘要生成成功！")
        print(f"📄 摘要内容 ({len(summary)} 字):")
        print(f"   {summary}")

        return True

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        return False


def test_generate_image_prompts():
    """测试2: 生成配图提示词"""
    print("\n" + "=" * 60)
    print("🧪 测试2: 生成配图提示词")
    print("=" * 60)
    print()

    article = """
# 2025年人工智能发展趋势

随着大模型技术的快速发展，人工智能正在各个行业带来深刻变革。
在医疗领域，AI辅助诊断系统能够帮助医生更准确地识别疾病。
在金融领域，智能风控系统大大提升了交易安全性。
在教育领域，个性化AI助教正在改变传统的教学模式。

未来几年，我们将看到更多AI技术的创新和应用。
"""

    title = "2025年人工智能发展趋势"

    print(f"📝 标题: {title}")
    print(f"📄 文章字数: {len(article)} 字")
    print()
    print("⏳ 正在生成配图提示词...")

    try:
        prompts = deepseek_client.generate_image_prompts(article, title)

        print()
        print("✅ 配图提示词生成成功！")
        print()

        print("🎨 封面图提示词:")
        for i, prompt in enumerate(prompts.get("cover_prompts", [])[:2], 1):
            print(f"   {i}. {prompt}")

        print()
        print("🖼️  插图提示词:")
        for i, prompt in enumerate(prompts.get("image_prompts", [])[:3], 1):
            print(f"   {i}. {prompt}")

        if prompts.get("style"):
            print()
            print(f"🎭 整体风格: {prompts['style']}")

        if prompts.get("color_scheme"):
            print(f"🎨 色彩方案: {prompts['color_scheme']}")

        return True

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_refine_content():
    """测试3: 优化文章内容"""
    print("\n" + "=" * 60)
    print("🧪 测试3: 优化文章内容")
    print("=" * 60)
    print()

    original = """
# Python教程

Python是一个编程语言。它有很多用途。我们可以用Python做数据分析。也可以做网站开发。
Python的语法很简单。很多人喜欢使用Python。
"""

    print(f"📝 原始内容 ({len(original)} 字):")
    print(f"   {original[:100]}...")
    print()
    print("⏳ 正在优化内容...")

    try:
        refined = deepseek_client.refine_content(original)

        print()
        print("✅ 内容优化成功！")
        print()
        print(f"📄 优化后内容 ({len(refined)} 字):")
        print(f"   {refined[:200]}...")

        return True

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        return False


def test_generate_chart_prompt():
    """测试4: 生成图表提示词"""
    print("\n" + "=" * 60)
    print("🧪 测试4: 生成图表提示词")
    print("=" * 60)
    print()

    article = """
# 2024年销售数据报告

本季度各产品线销售情况如下：
- 电子产品: 销售额500万元，同比增长20%
- 家居用品: 销售额300万元，同比增长15%
- 服装配饰: 销售额200万元，同比增长10%
- 食品饮料: 销售额400万元，同比增长25%

总体来看，各产品线都保持了良好的增长势头。
"""

    print(f"📝 文章字数: {len(article)} 字")
    print()
    print("⏳ 正在分析是否需要图表...")

    try:
        chart_config = deepseek_client.generate_chart_prompt(article)

        print()
        if chart_config:
            print("✅ 需要生成图表！")
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
            print("ℹ️  此文章不需要生成图表")

        return True

    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 60)
    print("🧪 DeepSeek 客户端功能测试")
    print("=" * 60)
    print()

    print(f"🤖 模型: {deepseek_client.model}")
    print(f"🌡️  温度: {deepseek_client.temperature}")
    print(f"📊 最大Token: {deepseek_client.max_tokens}")
    print()

    results = []

    # 运行所有测试
    results.append(("摘要生成", test_generate_summary()))
    results.append(("配图提示词", test_generate_image_prompts()))
    results.append(("内容优化", test_refine_content()))
    results.append(("图表提示词", test_generate_chart_prompt()))

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print()

    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} - {name}")

    total = len(results)
    passed = sum(1 for _, s in results if s)

    print()
    print(f"总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
