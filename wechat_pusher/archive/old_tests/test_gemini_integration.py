#!/usr/bin/env python3
"""
集成测试：Gemini自动图表数据查找

测试流程：
1. AI分析文章，智能插入图表占位符
2. 使用Gemini + Google Search查找真实数据
3. 自动生成图表
4. 发布到微信草稿箱
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.workflow.publisher import ArticlePublisher
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """运行集成测试"""
    logger.info("=" * 80)
    logger.info("🧪 Gemini自动图表数据查找 - 集成测试")
    logger.info("=" * 80)

    # 测试文章路径
    test_article = "test_gemini_auto_chart.md"

    logger.info(f"\n📄 测试文章: {test_article}")
    logger.info("-" * 80)

    try:
        # 直接调用publish方法，完整测试流程
        logger.info("\n🚀 开始完整发布流程...")
        publisher = ArticlePublisher(fixed_author="测试作者")
        success = publisher.publish(test_article)

        if success:
            logger.info("\n" + "=" * 80)
            logger.info("🎉 集成测试完成！")
            logger.info("=" * 80)
            logger.info("\n💡 下一步:")
            logger.info("  1. 登录微信公众号后台查看草稿")
            logger.info("  2. 检查图表数据是否准确")
            logger.info("  3. 检查图片是否正确嵌入")
            return 0
        else:
            logger.error("\n❌ 发布失败")
            return 1

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
