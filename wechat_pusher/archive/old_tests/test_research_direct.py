"""
直接调用tool_engine_local的研究助手
"""
import sys
import asyncio
import json
import os

# 切换到tool_engine_local目录
tool_engine_path = '/home/jsjrjft/project/tool_engine_local'
os.chdir(tool_engine_path)
sys.path.insert(0, tool_engine_path)

print(f"工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:3]}")

from src.tools.research_assistant import ResearchAssistantTool


async def test_research_assistant():
    """测试研究助手获取图表数据"""

    print("=" * 80)
    print("测试Research Assistant获取图表数据")
    print("=" * 80)

    # 创建研究助手实例
    research_tool = ResearchAssistantTool()

    # 测试查询
    test_queries = [
        {
            "name": "比特币可再生能源占比",
            "keywords": ["bitcoin", "renewable energy", "mining", "sustainable", "percentage"],
            "requirements": """
查找比特币挖矿中可再生能源占比的具体数值数据：

1. 时间范围：2019-2024年
2. 需要每年的确切百分比数值
3. 数据来源要可靠（如比特币矿业委员会BMC）
4. 如果有官方统计数据更好

请返回JSON格式：
{
  "source": "数据来源",
  "data": {
    "years": [2019, 2020, 2021, 2022, 2023, 2024],
    "percentages": [XX, XX, XX, XX, XX, XX]
  },
  "notes": "数据说明"
}

如果找不到完整数据，请明确说明缺失的年份。
"""
        },
        {
            "name": "比特币算力增长",
            "keywords": ["bitcoin", "hash rate", "hashrate", "EH/s", "network"],
            "requirements": """
查找比特币网络总算力增长的具体数值：

1. 时间范围：2020-2024年
2. 单位：EH/s (exahashes per second)
3. 需要每年的总算力数值
4. 数据来源要可靠

请返回JSON格式：
{
  "source": "数据来源",
  "data": {
    "years": [2020, 2021, 2022, 2023, 2024],
    "hash_rate": [XX, XX, XX, XX, XX]
  },
  "notes": "数据说明"
}
"""
        }
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"测试查询 {i}/{len(test_queries)}: {query['name']}")
        print('=' * 80)

        try:
            print(f"\n关键词: {', '.join(query['keywords'][:5])}")
            print("正在查询...")

            # 调用研究助手
            result = await research_tool.search(
                keywords=query['keywords'],
                requirements=query['requirements'],
                detail_level="comprehensive",
                speed_priority="thorough"
            )

            print("\n查询结果:")
            print("-" * 80)

            # 格式化输出
            if isinstance(result, dict):
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(result)

            print("-" * 80)

            # 分析结果
            if isinstance(result, dict):
                if result.get('results'):
                    print(f"\n✅ 成功获取 {len(result['results'])} 个结果")
                else:
                    print("\n⚠️  未找到结果")

                # 查找数据来源
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"状态: {metadata.get('status', 'N/A')}")
                    print(f"数据来源: {metadata.get('sources', 'N/A')}")

        except Exception as e:
            print(f"\n❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()

        # 等待间隔
        if i < len(test_queries):
            print("\n等待3秒...")
            await asyncio.sleep(3)

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(test_research_assistant())
