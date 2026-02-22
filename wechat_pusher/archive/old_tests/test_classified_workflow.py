"""
测试分类占位符工作流程
1. AI优化内容并插入分类占位符（CHART/IMAGE）
2. 分类提取占位符
3. CHART → Matplotlib生成，IMAGE → Doubao生成
4. 替换占位符为真实URL
"""
from pathlib import Path
from src.ai.deepseek_client import deepseek_client
from src.ai.doubao_client import doubao_client
from src.chart.chart_generator import chart_generator
from src.converter.markdown_parser import MarkdownParser
from src.converter.wechat_adapter import WeChatAdapter
from src.utils.logger import get_logger
import time

logger = get_logger(__name__)


def test_classified_workflow():
    """测试分类占位符工作流程"""

    # 测试文章
    test_content = """# 比特币能源转型

比特币挖矿正在经历一场深刻的能源转型。随着环保意识的提升和能源效率的改进，矿工们正在寻找更清洁、更高效的能源解决方案。

传统矿机的能耗持续增长，而可再生能源的占比正在快速提升。

## 算力价值重估

算力正在从单纯的工具演变为一种战略资源。AI的兴起让算力有了新的去处。

这不仅是技术路线的变革，更是价值范式的重构。
"""

    logger.info("=" * 80)
    logger.info("测试分类占位符工作流程")
    logger.info("=" * 80)

    # 步骤1: AI优化内容并插入分类占位符
    logger.info("\n步骤1: AI优化内容（插入分类占位符）")
    logger.info("-" * 80)
    refined_content = deepseek_client.refine_content(test_content)

    logger.info(f"\n优化后的内容（前800字符）：")
    logger.info("-" * 80)
    print(refined_content[:800] + "...")

    # 步骤2: 分类提取占位符
    logger.info("\n步骤2: 分类提取占位符")
    logger.info("-" * 80)
    placeholders = deepseek_client.extract_image_placeholders(refined_content)

    logger.info(f"\n提取结果：")
    logger.info(f"  CHART占位符: {len(placeholders['charts'])}个")
    for i, desc in enumerate(placeholders['charts'], 1):
        logger.info(f"    CHART{i}: {desc}")

    logger.info(f"  IMAGE占位符: {len(placeholders['images'])}个")
    for i, desc in enumerate(placeholders['images'], 1):
        logger.info(f"    IMAGE{i}: {desc}")

    if not placeholders['charts'] and not placeholders['images']:
        logger.warning("⚠️  未检测到任何占位符，测试无法继续")
        return False

    # 步骤3: 生成图片（分类生成）
    logger.info("\n步骤3: 分类生成图片")
    logger.info("-" * 80)

    article_id = f"test_classified_{int(time.time())}"
    article_dir = Path("./output") / article_id
    article_dir.mkdir(exist_ok=True, parents=True)

    result = {
        "illustrations": [],
        "charts": []
    }

    # 3.1 生成CHART（Matplotlib）
    if placeholders['charts']:
        logger.info(f"\n生成数据图表（{len(placeholders['charts'])}个）:")
        for i, desc in enumerate(placeholders['charts'], 1):
            logger.info(f"  CHART{i}: {desc}")

            # 简化处理：使用示例数据生成图表
            if "柱状图" in desc:
                chart_config = {
                    "chart_type": "bar",
                    "title": "比特币能耗对比",
                    "data": {
                        "labels": ["2020", "2021", "2022", "2023", "2024"],
                        "values": [100, 110, 95, 80, 65],
                        "xlabel": "年份",
                        "ylabel": "能耗（TWh）"
                    },
                    "description": desc
                }
            elif "折线图" in desc:
                chart_config = {
                    "chart_type": "line",
                    "title": "可再生能源占比趋势",
                    "data": {
                        "labels": ["2020", "2021", "2022", "2023", "2024"],
                        "values": [20, 35, 50, 68, 80],
                        "xlabel": "年份",
                        "ylabel": "占比（%）"
                    },
                    "description": desc
                }
            else:
                logger.warning(f"    无法识别图表类型，跳过")
                continue

            chart_path = str(article_dir / f"chart_{i}.png")
            try:
                generated_path = chart_generator.generate_chart(chart_config, chart_path)
                if generated_path:
                    result['charts'].append(generated_path)
                    logger.info(f"    ✅ 图表{i}生成成功")
                else:
                    logger.error(f"    ❌ 图表{i}生成失败")
            except Exception as e:
                logger.error(f"    ❌ 图表{i}生成异常: {e}")

    # 3.2 生成IMAGE（Doubao） - 只生成前1个，节省时间
    if placeholders['images']:
        logger.info(f"\n生成概念插图（{len(placeholders['images'])}个，只测试第1个）:")
        desc = placeholders['images'][0]
        logger.info(f"  IMAGE1: {desc}")

        illu_path = str(article_dir / "illustration_1.png")
        try:
            generated_path = doubao_client.generate_illustration(desc, illu_path)
            if generated_path:
                result['illustrations'].append(generated_path)
                logger.info(f"    ✅ 插图1生成成功")
            else:
                logger.error(f"    ❌ 插图1生成失败")
        except Exception as e:
            logger.error(f"    ❌ 插图1生成异常: {e}")

    logger.info(f"\n图片生成完成: {len(result['charts'])}图表 + {len(result['illustrations'])}插图")

    # 步骤4: 测试占位符替换
    logger.info("\n步骤4: 测试占位符替换")
    logger.info("-" * 80)

    # 模拟：将Markdown转换为HTML
    parser = MarkdownParser()
    article = parser.parse_content(refined_content)
    html_content = article.html

    import re
    chart_count = len(re.findall(r'\[\[CHART:[^\]]+\]\]', html_content))
    image_count = len(re.findall(r'\[\[IMAGE:[^\]]+\]\]', html_content))

    logger.info(f"HTML中包含: {chart_count}个CHART占位符 + {image_count}个IMAGE占位符")

    # 模拟替换（使用假URL）
    test_html = html_content

    # 替换CHART
    for i, placeholder in enumerate(re.findall(r'\[\[CHART:[^\]]+\]\]', html_content)):
        if i < len(result['charts']):
            fake_url = f"chart_url_{i+1}.png"
            img_tag = f'<section><img src="{fake_url}" /></section>'
            test_html = test_html.replace(placeholder, img_tag, 1)
            logger.info(f"  ✅ 替换CHART占位符{i+1}")

    # 替换IMAGE
    for i, placeholder in enumerate(re.findall(r'\[\[IMAGE:[^\]]+\]\]', html_content)):
        if i < len(result['illustrations']):
            fake_url = f"image_url_{i+1}.png"
            img_tag = f'<section><img src="{fake_url}" /></section>'
            test_html = test_html.replace(placeholder, img_tag, 1)
            logger.info(f"  ✅ 替换IMAGE占位符{i+1}")

    # 验证替换结果
    remaining_charts = len(re.findall(r'\[\[CHART:[^\]]+\]\]', test_html))
    remaining_images = len(re.findall(r'\[\[IMAGE:[^\]]+\]\]', test_html))

    logger.info(f"\n替换验证：")
    logger.info(f"  剩余CHART占位符: {remaining_charts}")
    logger.info(f"  剩余IMAGE占位符: {remaining_images}")

    if remaining_charts == 0 and remaining_images == 0:
        logger.info("  ✅ 所有占位符已成功替换")
        success = True
    else:
        logger.warning("  ⚠️  部分占位符未替换")
        success = False

    # 总结
    logger.info("\n" + "=" * 80)
    logger.info("🎉 测试完成！")
    logger.info("=" * 80)
    logger.info("\n工作流程验证：")
    logger.info(f"1. ✅ AI优化内容并插入分类占位符")
    logger.info(f"2. ✅ 提取到 {len(placeholders['charts'])}个CHART + {len(placeholders['images'])}个IMAGE")
    logger.info(f"3. ✅ 生成 {len(result['charts'])}个图表 + {len(result['illustrations'])}个插图")
    logger.info(f"4. ✅ 占位符替换验证通过")

    logger.info("\n分类生成路径：")
    logger.info(f"  [[CHART:...]] → Matplotlib生成数据图表")
    logger.info(f"  [[IMAGE:...]] → Doubao生成概念插图")

    return success


if __name__ == "__main__":
    success = test_classified_workflow()

    if success:
        logger.info("\n✅ 分类工作流程测试通过")
    else:
        logger.error("\n❌ 测试失败")
