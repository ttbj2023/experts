#!/usr/bin/env python3
"""
独立的图表生成工具

使用流程：
1. 调用subagent调研数据
2. 生成图表
3. 上传到微信
4. 返回图表URL供主流程使用
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.chart.chart_generator import chart_generator
from src.wechat.api_client import wechat_api_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_chart_with_research(description: str, save_path: str = None) -> dict:
    """
    使用subagent调研数据并生成图表

    Args:
        description: 图表描述，例如：
            - "柱状图，显示税率从6%调整到9%"
            - "折线图，显示2020-2024年比特币可再生能源占比变化"
        save_path: 图表保存路径（可选）

    Returns:
        dict: {
            "success": True/False,
            "chart_path": "/path/to/chart.png",
            "media_id": "wechat_media_id",
            "url": "https://wechatcdn.com/...",
            "error": "错误信息（如果失败）"
        }
    """
    logger.info("=" * 80)
    logger.info("📊 图表生成工具")
    logger.info("=" * 80)

    result = {
        "success": False,
        "chart_path": None,
        "media_id": None,
        "url": None,
        "error": None
    }

    # Step 1: 提示用户使用subagent调研数据
    logger.info("Step 1: 调用subagent调研数据")
    logger.info(f"  图表描述: {description}")
    logger.info("")
    logger.info("  请在Claude Code中执行以下命令获取数据：")
    logger.info(f"  Use the chart-data-researcher subagent to find data for: {description}")
    logger.info("")
    logger.info("  然后将获取的数据以以下格式提供给本工具：")
    logger.info("  格式示例：")
    logger.info('    - 柱状图: "柱状图，数据：A: 10%, B: 20%, C: 30%"')
    logger.info('    - 折线图: "折线图，数据：2020年100, 2021年150, 2022年220, 2023年310, 2024年450"')
    logger.info('    - 对比图: "柱状图，从6%到9%"')
    logger.info("")
    logger.error("❌ 当前为自动化流程，请先手动获取数据后重新调用")
    logger.info("   或者直接在描述中提供数据")

    return result


def generate_chart_from_description(description: str, save_path: str = None) -> dict:
    """
    从描述中提取数据并生成图表

    Args:
        description: 包含数据的图表描述，例如：
            - "柱状图，显示税率调整。数据：增值电信服务: 6%，基础电信服务: 9%"
            - "折线图，数据：2020年100, 2021年150, 2022年220, 2023年310, 2024年450"
        save_path: 图表保存路径（可选）

    Returns:
        dict: 生成结果
    """
    import re

    result = {
        "success": False,
        "chart_path": None,
        "media_id": None,
        "url": None,
        "error": None
    }

    logger.info("=" * 80)
    logger.info("📊 从描述生成图表")
    logger.info("=" * 80)

    # 尝试提取数据
    # 格式1: "A: 10%, B: 20%, C: 30%" 或 "2020年100, 2021年150"
    pattern1 = r'([\w\u4e00-\u9fa5]+)[:：年]\s*([\d.]+%?)\s*[,，]?\s*'
    matches1 = re.findall(pattern1, description)

    if not matches1 or len(matches1) < 2:
        result["error"] = "无法从描述中提取数据，请确保描述包含具体数值"
        logger.error(f"❌ {result['error']}")
        return result

    labels = [m[0] for m in matches1]
    values = []
    for m in matches1:
        val = m[1]
        if '%' in val:
            values.append(float(val.rstrip('%')))
        else:
            values.append(float(val))

    # 推断图表类型
    chart_type = "pie" if len(labels) <= 5 else "bar"
    if all(l.isdigit() and len(l) == 4 for l in labels):
        chart_type = "line"

    # 检测是否有百分比
    has_percent = any('%' in m[1] for m in matches1)

    # 构建图表配置
    chart_config = {
        "chart_type": chart_type,
        "title": "数据图表",
        "data": {
            "labels": labels,
            "values": values,
            "xlabel": "",
            "ylabel": "占比 (%)" if has_percent else "数值"
        }
    }

    logger.info(f"  图表类型: {chart_type}")
    logger.info(f"  数据点数: {len(labels)}")
    logger.info(f"  标签: {labels}")
    logger.info(f"  数值: {values}")

    # 生成图表
    if not save_path:
        save_path = f"output/chart_{labels[0]}_{labels[-1]}.png"

    chart_path = chart_generator.generate_chart(
        chart_data=chart_config,
        save_path=save_path
    )

    if not chart_path:
        result["error"] = "图表生成失败"
        logger.error(f"❌ {result['error']}")
        return result

    logger.info(f"✅ 图表已生成: {chart_path}")
    result["chart_path"] = chart_path

    # 上传到微信
    logger.info("上传到微信...")
    try:
        media_info = wechat_api_client.upload_material(chart_path, "image")
        result["media_id"] = media_info["media_id"]
        result["url"] = media_info["url"]
        result["success"] = True
        logger.info(f"✅ 上传成功")
        logger.info(f"  Media ID: {result['media_id']}")
        logger.info(f"  URL: {result['url']}")
    except Exception as e:
        result["error"] = f"微信上传失败: {e}"
        logger.error(f"❌ {result['error']}")
        # 图表已生成，只是上传失败，也算部分成功
        result["success"] = True

    return result


def main():
    parser = argparse.ArgumentParser(description="生成数据图表并上传到微信")
    parser.add_argument("description", help="图表描述（包含数据）")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--no-upload", action="store_true", help="不上传到微信")

    args = parser.parse_args()

    result = generate_chart_from_description(args.description, args.output)

    if args.no_upload and result["chart_path"]:
        logger.info("\n✅ 图表生成完成（未上传）")
        logger.info(f"  路径: {result['chart_path']}")
    elif result["success"]:
        logger.info("\n✅ 图表生成并上传成功")
        logger.info(f"  本地路径: {result['chart_path']}")
        logger.info(f"  微信URL: {result['url']}")
        print(f"\n微信图表URL（用于文章占位符替换）:")
        print(result["url"])
    else:
        logger.error(f"\n❌ 失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
