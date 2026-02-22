"""
测试使用research_assistant查找图表数据
验证其返回数据的准确性和可用性
"""
from mcp__tool_engine_local__research_assistant import research_assistant
from src.utils.logger import get_logger
import json
import re

logger = get_logger(__name__)


def test_chart_data_research():
    """测试图表数据研究"""

    logger.info("=" * 80)
    logger.info("测试使用research_assistant查找图表数据")
    logger.info("=" * 80)

    # 测试案例1：比特币能耗数据
    test_cases = [
        {
            "name": "比特币可再生能源占比",
            "description": "折线图，横轴为年份（2019-2024），纵轴为占比（%）。显示比特币挖矿中可再生能源占比的变化趋势",
            "keywords": ["bitcoin", "renewable energy", "mining", "sustainable energy percentage"],
            "context": "关于比特币挖矿能源转型的文章"
        },
        {
            "name": "比特币算力增长",
            "description": "折线图，横轴为年份（2019-2024），纵轴为算力（EH/s）。显示全球比特币算力总量增长趋势",
            "keywords": ["bitcoin", "hash rate", "hashrate", "network computing power"],
            "context": "关于比特币网络发展的文章"
        },
        {
            "name": "挖矿能源成本",
            "description": "柱状图，对比不同能源类型的挖矿成本（美元/kWh）",
            "keywords": ["bitcoin mining", "electricity cost", "energy price", "mining profitability"],
            "context": "关于挖矿经济性的分析"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"测试案例 {i}/{len(test_cases)}: {case['name']}")
        logger.info('=' * 80)

        logger.info(f"描述: {case['description']}")
        logger.info(f"关键词: {', '.join(case['keywords'])}")

        try:
            # 调用research_assistant
            logger.info("\n正在查询数据...")
            result = research_assistant(
                keywords=case['keywords'],
                requirements=f"""
请查找以下具体数值数据用于生成图表：

图表描述：{case['description']}

文章背景：{case['context']}

数据要求：
1. 返回精确的数值数据（不能是估算或推测）
2. 提供数据来源和发布时间
3. 如果是官方统计数据更好
4. 格式要求：返回JSON格式
   {{
     "data_type": "时间序列/对比数据",
     "source": "数据来源",
     "last_updated": "数据时间",
     "chart_data": {{
       "labels": ["年份/类别1", "年份/类别2", ...],
       "values": [数值1, 数值2, ...],
       "xlabel": "X轴标签",
       "ylabel": "Y轴标签"
     }},
     "notes": "数据说明或限制"
   }}

5. 如果找不到准确数据，请明确说明"无可用数据"，不要编造数值
6. 如果找到的数据不完整（例如缺少某些年份），请说明缺失情况
""",
                detail_level="comprehensive",  # 获取更详细的信息
                speed_priority="thorough"       # 牺牲速度保证质量
            )

            logger.info(f"\n查询结果：")
            logger.info("-" * 80)
            print(result)
            logger.info("-" * 80)

            # 尝试解析JSON
            parsed = parse_research_result(result)
            if parsed:
                logger.info(f"\n✅ 成功解析数据：")
                logger.info(f"  数据类型: {parsed.get('data_type', 'N/A')}")
                logger.info(f"  数据来源: {parsed.get('source', 'N/A')}")
                logger.info(f"  更新时间: {parsed.get('last_updated', 'N/A')}")
                logger.info(f"  数据点数量: {len(parsed.get('chart_data', {}).get('values', []))}")
            else:
                logger.warning(f"\n⚠️  无法从结果中提取结构化数据")

        except Exception as e:
            logger.error(f"\n❌ 查询失败: {e}")

        # 添加分隔，避免混淆
        if i < len(test_cases):
            print("\n" + "=" * 80)
            print("等待3秒后进行下一个测试...")
            print("=" * 80 + "\n")
            import time
            time.sleep(3)

    logger.info("\n" + "=" * 80)
    logger.info("测试完成")
    logger.info("=" * 80)


def parse_research_result(result: str) -> dict:
    """
    尝试从研究助手返回的结果中提取JSON数据

    Args:
        result: research_assistant返回的文本

    Returns:
        dict: 解析后的数据，失败返回None
    """
    # 方法1：查找JSON代码块
    json_pattern = r'```(?:json)?\s*\n?(\{.*?\})\s?\n?```'
    match = re.search(json_pattern, result, re.DOTALL)

    if match:
        try:
            data = json.loads(match.group(1))
            return data
        except json.JSONDecodeError:
            pass

    # 方法2：查找裸JSON对象
    json_pattern2 = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern2, result)

    for match in matches:
        try:
            data = json.loads(match)
            # 验证是否包含chart_data
            if 'chart_data' in data:
                return data
        except json.JSONDecodeError:
            continue

    # 方法3：查找关键数据模式（fallback）
    # 例如：2020: 45%, 2021: 52%, ...
    logger.warning("无法找到JSON格式，尝试提取文本中的数值模式...")
    return None


def test_simple_query():
    """简单的数据查询测试"""
    logger.info("\n" + "=" * 80)
    logger.info("简单查询测试：比特币可再生能源占比（2020-2024）")
    logger.info("=" * 80)

    result = research_assistant(
        keywords=["bitcoin", "renewable energy", "mining", "2024", "percentage"],
        requirements="""
查找具体的数值数据：
- 比特币挖矿中可再生能源的占比（百分比）
- 时间范围：2020年至2024年
- 需要确切数值，来源可靠

返回格式：
2020年: XX%
2021年: XX%
2022年: XX%
2023年: XX%
2024年: XX%

请提供数据来源。
""",
        detail_level="standard"
    )

    print("\n查询结果：")
    print("-" * 80)
    print(result)
    print("-" * 80)


if __name__ == "__main__":
    # 先运行简单测试
    test_simple_query()

    print("\n\n" + "=" * 80)
    print("开始完整测试")
    print("=" * 80 + "\n")

    # 再运行完整测试
    test_chart_data_research()
