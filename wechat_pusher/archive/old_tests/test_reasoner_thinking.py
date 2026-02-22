"""
测试DeepSeek Reasoner的思考过程
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from openai import OpenAI
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("=" * 80)
    print("🧠 测试DeepSeek Reasoner - 查看思考过程")
    print("=" * 80)
    print()

    # 初始化客户端（不使用deepseek_client，直接调用API）
    client = OpenAI(
        api_key=config.deepseek.api_key,
        base_url=config.deepseek.base_url,
    )

    model = "deepseek-reasoner"
    article = """
    比特币正面临一场深刻的生存危机。AI算力凭借更高的能源变现效率和资本吸引力，
    正在系统性挤压比特币赖以生存的物理基础——全球分散的算力网络。
    """

    print(f"🤖 模型: {model}")
    print(f"📝 原文: {article.strip()}")
    print()
    print("⏳ 正在调用API...")
    print()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的内容创作助手。"
                },
                {
                    "role": "user",
                    "content": f"请为以下文章生成一个30字以内的摘要：\n{article}"
                },
            ],
            temperature=0.7,
            max_tokens=8000,
        )

        raw_content = response.choices[0].message.content
        raw_length = len(raw_content)

        print("-" * 80)
        print("📄 原始响应（包含思考过程）:")
        print("-" * 80)
        print(raw_content)
        print()
        print("-" * 80)
        print(f"📊 原始响应长度: {raw_length} 字符")
        print("-" * 80)
        print()

        # 提取最终答案
        thinking_start = raw_content.find("<thinking>")
        thinking_end = raw_content.find("</thinking>")

        if thinking_start != -1 and thinking_end != -1:
            thinking_content = raw_content[thinking_start + len("<thinking>"):thinking_end].strip()
            final_answer = raw_content[thinking_end + len("</thinking>"):].strip()

            print("🧠 思考过程:")
            print("-" * 80)
            print(thinking_content)
            print()
            print("-" * 80)
            print(f"✅ 最终摘要 ({len(final_answer)}字 / {len(final_answer.encode('utf-8'))}字节):")
            print("-" * 80)
            print(final_answer)
        else:
            print("ℹ️  未检测到<thinking>标签，可能是普通模型")

        print()
        print("=" * 80)
        print("💡 推理模型优势:")
        print("  1. 展示思考过程，可追溯推理逻辑")
        print("  2. 更深入理解任务要求")
        print("  3. 输出质量通常更高")
        print("  4. 适合复杂任务")
        print()
        print("⚠️  注意事项:")
        print("  1. 响应时间更长（需要思考）")
        print("  2. Token消耗更大（包含思考过程）")
        print("  3. 需要提取最终答案（去除<thinking>标签）")
        print("=" * 80)

    except Exception as e:
        print(f"❌ 调用失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
