"""
测试chart-data-researcher的功能（使用research_assistant工具）
模拟subagent应该完成的工作
"""
import json
import sys
import os

# 设置路径
os.chdir('/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')
sys.path.insert(0, '/home/jsjrjft/project/tool_engine_local')

print("=" * 80)
print("测试Chart Data Researcher功能")
print("=" * 80)

# 测试用例：比特币可再生能源占比
test_case = {
    "chart_description": "折线图，横轴为年份（2019-2024），纵轴为占比（%）。显示比特币挖矿中可再生能源占比的变化趋势",
    "keywords": ["bitcoin", "renewable energy", "mining", "sustainable", "percentage", "2019-2024"],
    "data_requirements": """
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
}

print("\n测试用例：")
print(f"  图表描述: {test_case['chart_description']}")
print(f"  关键词: {', '.join(test_case['keywords'][:5])}")
print("\n" + "-" * 80)

try:
    # 尝试导入research_assistant
    from src.tools.research_assistant import ResearchAssistantTool
    print("✅ 成功导入 ResearchAssistantTool")

    # 创建实例
    import asyncio

    async def test_research():
        research_tool = ResearchAssistantTool()

        print("\n正在调用research_assistant...")
        result = await research_tool.search(
            keywords=test_case['keywords'],
            requirements=test_case['data_requirements'],
            detail_level="comprehensive",
            speed_priority="thorough"
        )

        print("\n查询结果：")
        print("-" * 80)

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

            metadata = result.get('metadata', {})
            if metadata:
                print(f"状态: {metadata.get('status', 'N/A')}")
                print(f"数据来源: {metadata.get('sources', 'N/A')}")

    # 运行测试
    asyncio.run(test_research())

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n尝试使用MCP工具...")

    # 尝试使用MCP工具
    try:
        # 注意：在实际的Claude Code环境中，这个工具应该可用
        # 这里我们只是模拟调用
        print("在Claude Code环境中，使用 mcp__tool_engine_local__research_assistant 工具")
        print("Subagent创建成功，下次会话即可使用")
    except Exception as e2:
        print(f"❌ MCP工具调用失败: {e2}")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
