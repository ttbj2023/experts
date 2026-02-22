"""
使用research_assistant找到的真实数据生成图表
"""
from pathlib import Path
from src.chart.chart_generator import chart_generator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_chart_with_real_data():
    """使用真实数据生成图表"""

    logger.info("=" * 80)
    logger.info("使用真实数据生成图表测试")
    logger.info("=" * 80)

    # research_assistant查找到的真实数据
    real_data = {
        "found": True,
        "chart_data": {
            "type": "line",
            "title": "比特币挖矿可再生能源占比变化（2019-2024）",
            "labels": ["2019", "2020", "2021", "2022", "2023", "2024"],
            "values": [74.1, 41.15, 28.48, 58.9, 59.9, 56.2],
            "xlabel": "年份",
            "ylabel": "可再生能源占比 (%)",
            "units": "%"
        },
        "source": "比特币矿业委员会 (BMC), 剑桥大学替代金融中心 (CCAF), Coinshares",
        "notes": "数据说明：可再生能源包括水电、风能、太阳能等。某些年份使用的是可持续能源数据（包含核能）。"
    }

    logger.info("\n数据来源：")
    logger.info(f"  {real_data['source']}")
    logger.info("\n数据点：")
    for year, pct in zip(real_data['chart_data']['labels'], real_data['chart_data']['values']):
        logger.info(f"  {year}: {pct}%")

    # 创建图表配置
    chart_data = {
        "chart_type": real_data['chart_data']['type'],
        "title": real_data['chart_data']['title'],
        "data": {
            "labels": real_data['chart_data']['labels'],
            "values": real_data['chart_data']['values'],
            "xlabel": real_data['chart_data']['xlabel'],
            "ylabel": real_data['chart_data']['ylabel']
        },
        "description": "使用research_assistant找到的真实数据",
        "source": real_data['source'],
        "notes": real_data['notes']
    }

    # 生成图表
    logger.info("\n" + "=" * 80)
    logger.info("生成图表...")
    logger.info("=" * 80)

    output_dir = Path("output/test_real_data_chart")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "bitcoin_renewable_energy.png"

    try:
        generated_path = chart_generator.generate_chart(
            chart_data=chart_data,
            save_path=str(output_path)
        )

        if generated_path:
            logger.info(f"\n✅ 图表生成成功！")
            logger.info(f"   保存路径: {generated_path}")

            # 验证文件
            if Path(generated_path).exists():
                file_size = Path(generated_path).stat().st_size
                logger.info(f"   文件大小: {file_size} 字节")

            logger.info("\n" + "=" * 80)
            logger.info("✅ 测试完成")
            logger.info("=" * 80)

            return {
                "success": True,
                "path": generated_path,
                "data_points": len(real_data['chart_data']['values']),
                "source": real_data['source']
            }
        else:
            logger.error("❌ 图表生成失败")
            return {"success": False, "error": "生成失败"}

    except Exception as e:
        logger.error(f"❌ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = test_chart_with_real_data()

    if result["success"]:
        print("\n✅ 图表生成成功！")
        print(f"路径: {result['path']}")
        print(f"数据点: {result['data_points']} 个")
        print(f"来源: {result['source']}")
    else:
        print(f"\n❌ 生成失败: {result.get('error', 'Unknown error')}")
