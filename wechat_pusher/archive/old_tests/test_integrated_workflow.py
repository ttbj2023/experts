"""
测试完整的工作流：CHART占位符 + 数据研究 + 图表生成
"""
from pathlib import Path
from src.workflow.publisher import ArticlePublisher
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_workflow_with_chart_placeholder():
    """测试包含CHART占位符的完整工作流"""

    logger.info("=" * 80)
    logger.info("测试CHART占位符 + 数据研究工作流")
    logger.info("=" * 80)

    # 创建测试文章
    test_article = """# 比特币挖矿的能源转型

比特币挖矿正在经历一场能源革命。

[[CHART:折线图，横轴为年份（2019-2024），纵轴为占比（%）。显示比特币挖矿中可再生能源占比的变化趋势]]

近年来，越来越多的矿工转向使用可再生能源。

[[IMAGE:一个太阳能板旁边的矿机设备，阳光明媚的场景]]

这一转变不仅有助于环境保护，也提高了 mining 的可持续性。
"""

    # 保存测试文章
    test_file = Path("test_chart_article.md")
    test_file.write_text(test_article, encoding='utf-8')
    logger.info(f"✅ 创建测试文章: {test_file}")

    # 创建发布器
    publisher = ArticlePublisher()

    try:
        # Step 1: 读取文章内容
        logger.info("\n" + "=" * 80)
        logger.info("Step 1: 读取文章内容")
        logger.info("=" * 80)

        article_content = test_file.read_text(encoding='utf-8')
        logger.info(f"✅ 文章读取成功")
        logger.info(f"   内容长度: {len(article_content)} 字符")

        # Step 2: AI分析（包含占位符提取）
        logger.info("\n" + "=" * 80)
        logger.info("Step 2: AI分析内容优化")
        logger.info("=" * 80)

        # 创建一个简单的article对象用于测试
        from src.converter.markdown_parser import MarkdownParser
        parser = MarkdownParser()
        article = parser.parse_file(test_file)

        ai_result = publisher.analyze_with_ai(article.title, article.content)
        logger.info(f"✅ AI分析完成")

        placeholders = ai_result.get("placeholders", {})
        logger.info(f"   CHART占位符: {len(placeholders.get('charts', []))} 个")
        logger.info(f"   IMAGE占位符: {len(placeholders.get('images', []))} 个")

        for i, chart_desc in enumerate(placeholders.get('charts', []), 1):
            logger.info(f"   图表{i}: {chart_desc}")

        # Step 3: 生成图片（包括数据研究）
        logger.info("\n" + "=" * 80)
        logger.info("Step 3: 生成图片（数据研究 + 图表生成）")
        logger.info("=" * 80)

        article_id = "test_chart_workflow"
        images = publisher.generate_images(ai_result, article_id)

        logger.info(f"✅ 图片生成完成:")
        logger.info(f"   封面图: {len(images['covers'])} 张")
        logger.info(f"   插图: {len(images['illustrations'])} 张")
        logger.info(f"   图表: {len(images['charts'])} 张")

        # Step 4: 上传图片到微信并嵌入
        logger.info("\n" + "=" * 80)
        logger.info("Step 4: 上传图片到微信并嵌入")
        logger.info("=" * 80)

        # 上传图片到微信获取media_id和url
        media_infos = publisher.upload_media_to_wechat(images)

        # 嵌入到HTML
        html_content = publisher._embed_images(article.html, media_infos)

        logger.info(f"✅ 图片嵌入完成")
        logger.info(f"   HTML长度: {len(html_content)} 字符")

        # 保存结果
        output_dir = Path("output") / article_id
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "article.html"
        output_file.write_text(html_content, encoding='utf-8')
        logger.info(f"✅ HTML已保存: {output_file}")

        # 显示结果摘要
        logger.info("\n" + "=" * 80)
        logger.info("测试结果摘要")
        logger.info("=" * 80)
        logger.info(f"✅ 成功生成HTML文章")
        logger.info(f"   输出目录: {output_dir}")
        logger.info(f"   封面图: {len(images['covers'])}")
        logger.info(f"   插图: {len(images['illustrations'])}")
        logger.info(f"   图表: {len(images['charts'])}")

        # 检查是否有占位符被替换
        placeholder_count = html_content.count("[[CHART:") + html_content.count("[[IMAGE:")
        if placeholder_count > 0:
            logger.warning(f"⚠️  还有 {placeholder_count} 个占位符未被替换")
        else:
            logger.info("✅ 所有占位符已成功替换为图片")

        logger.info("\n" + "=" * 80)
        logger.info("✅ 测试完成")
        logger.info("=" * 80)

        return {
            "success": True,
            "output_dir": str(output_dir),
            "images": images,
            "placeholder_count": placeholder_count
        }

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    result = test_workflow_with_chart_placeholder()

    if result["success"]:
        print("\n✅ 测试成功！")
        print(f"输出目录: {result['output_dir']}")
        print(f"图片统计: 封面{result['images']['covers']}, "
              f"插图{result['images']['illustrations']}, "
              f"图表{result['images']['charts']}")
        if result['placeholder_count'] == 0:
            print("✅ 所有占位符已替换")
        else:
            print(f"⚠️  还有 {result['placeholder_count']} 个占位符未替换")
    else:
        print(f"\n❌ 测试失败: {result.get('error', 'Unknown error')}")
