"""
测试更新后的DeepSeek提示词
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.ai.deepseek_client import deepseek_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("=" * 80)
    print("🧪 测试更新后的DeepSeek提示词")
    print("=" * 80)
    print()

    # 测试文章
    title = "当算力有了更好的去处：比特币的物理防线正在解体"
    content = """
比特币正面临一场深刻的生存危机。AI算力凭借更高的能源变现效率和资本吸引力，
正在系统性挤压比特币赖以生存的物理基础——全球分散的算力网络。

这场竞争的本质是能源与资本的效率革命。单位能源、单位硅晶圆面积所能产生的稳定现金流，
AI计算已呈现数量级优势。资本和资源持续流向效率更高的地方，是不可逆的长期趋势。

比特币挖矿业内部正在发生结构性变化：矿企向AI基础设施转型，算力加速向寡头集中，
网络的去中心化与抗审查属性面临根本性挑战。
"""

    print(f"📝 测试文章:")
    print(f"   标题: {title}")
    print(f"   字数: {len(content)} 字")
    print()
    print(f"🤖 模型: {deepseek_client.model}")
    print(f"📏 最大Token: {deepseek_client.max_tokens}")
    print(f"🌡️  温度: {deepseek_client.temperature}")
    print(f"🧠 推理模式: {deepseek_client.is_reasoner}")
    print()

    results = []

    # 测试1: 生成摘要
    print("=" * 80)
    print("📋 测试1: 生成摘要（洞察风格）")
    print("=" * 80)
    print()
    try:
        summary = deepseek_client.generate_summary(content)
        print(f"✅ 摘要生成成功 ({len(summary)}字符):")
        print(f"   {summary}")
        print()
        results.append(("摘要", True))
    except Exception as e:
        print(f"❌ 失败: {e}")
        results.append(("摘要", False))

    # 测试2: 生成配图提示词
    print("=" * 80)
    print("🎨 测试2: 生成配图提示词（深度科技风格）")
    print("=" * 80)
    print()
    try:
        prompts = deepseek_client.generate_image_prompts(content, title)
        print(f"✅ 配图提示词生成成功:")
        print(f"   封面图: {len(prompts.get('cover_prompts', []))}个")
        print(f"   插图: {len(prompts.get('image_prompts', []))}个")
        print()
        print("   封面图提示词:")
        for i, prompt in enumerate(prompts.get('cover_prompts', []), 1):
            preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
            print(f"      {i}. {preview}")
        print()
        print(f"   整体风格: {prompts.get('style', 'N/A')}")
        print()
        results.append(("配图提示词", True))
    except Exception as e:
        print(f"❌ 失败: {e}")
        results.append(("配图提示词", False))

    # 测试3: 生成图表提示词
    print("=" * 80)
    print("📊 测试3: 生成图表提示词（专业数据风格）")
    print("=" * 80)
    print()
    try:
        chart = deepseek_client.generate_chart_prompt(content)
        if chart:
            print(f"✅ 需要生成图表:")
            print(f"   类型: {chart['chart_type']}")
            print(f"   标题: {chart['title']}")
            print(f"   数据维度: {len(chart['data']['labels'])}个")
        else:
            print("ℹ️  无需生成图表")
        print()
        results.append(("图表提示词", True))
    except Exception as e:
        print(f"❌ 失败: {e}")
        results.append(("图表提示词", False))

    # 测试4: 优化内容
    print("=" * 80)
    print("✏️  测试4: 优化内容（不说教风格）")
    print("=" * 80)
    print()
    try:
        refined = deepseek_client.refine_content(content)
        print(f"✅ 内容优化成功:")
        print(f"   原始: {len(content)}字")
        print(f"   优化后: {len(refined)}字")
        print()
        print("   优化后内容预览:")
        print("   " + "-" * 76)
        print("   " + refined[:300] + "...")
        print("   " + "-" * 76)
        print()
        results.append(("内容优化", True))
    except Exception as e:
        print(f"❌ 失败: {e}")
        results.append(("内容优化", False))

    # 总结
    print("=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    print()

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    total = len(results)
    passed = sum(1 for _, s in results if s)

    print()
    print(f"总计: {passed}/{total} 测试通过")

    if passed == total:
        print()
        print("🎉 所有测试通过！提示词更新成功！")
        print()
        print("💡 风格特点:")
        print("   ✅ 洞察深刻（体现核心观点）")
        print("   ✅ 启发思考（不说教）")
        print("   ✅ 专业克制（不花哨）")
        print("   ✅ 面向专业读者（非泛流量）")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
