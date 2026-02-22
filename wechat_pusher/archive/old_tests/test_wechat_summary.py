"""
测试微信摘要生成（50字/120字符限制）
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.ai.deepseek_client import deepseek_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("=" * 80)
    print("🧪 测试微信摘要生成（50字/120字符限制）")
    print("=" * 80)
    print()

    # 加载Bitcoin文章
    with open('/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher/bitcoin_article_draft.md', 'r', encoding='utf-8') as f:
        article = f.read()

    print(f"📄 原文章字数: {len(article)} 字")
    print()
    print("⏳ 正在生成50字以内的摘要...")
    print()

    # 测试默认的50字限制
    summary = deepseek_client.generate_summary(article)

    print("✅ 摘要生成成功！")
    print()
    print(f"📝 摘要内容 ({len(summary)} 字符):")
    print(f"   {summary}")
    print()

    # 验证是否符合微信限制
    char_count = len(summary)

    print("📊 验证结果:")
    print(f"   字符数: {char_count} 字符")
    print(f"   限制: 50字（目标）/ 120字符（微信硬上限）")
    print()

    if char_count <= 50:
        print("✅ 符合50字目标")
    elif char_count <= 120:
        print(f"⚠️  超出50字目标，但在微信120字符限制内")
    else:
        print(f"❌ 超出微信120字符硬限制！")

    print()
    print("-" * 80)
    print()

    # 多次测试，验证稳定性
    print("🧪 多次生成测试（验证50字限制的稳定性）:")
    print()

    for i in range(3):
        test_summary = deepseek_client.generate_summary(article)
        actual_chars = len(test_summary)

        if actual_chars == 0:
            status = "❌ 失败（超长返回空）"
        elif actual_chars <= 50:
            status = f"✅ {actual_chars}字符"
        else:
            status = f"⚠️  {actual_chars}字符（超长）"

        print(f"测试{i+1}: {status}")
        print(f"   {test_summary}")
        print()


if __name__ == "__main__":
    main()
