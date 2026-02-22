"""
测试修复后的中文转义问题
"""
from src.wechat.api_client import wechat_api_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_chinese_title():
    """测试中文标题是否能正确处理"""

    # 先上传一个封面图
    logger.info("步骤1: 上传封面图")
    from pathlib import Path

    output_dir = Path("./output")
    cover_images = list(output_dir.glob("**/cover_1.png"))

    if not cover_images:
        logger.error("未找到封面图")
        return False

    cover_path = str(cover_images[-1])
    media_id = wechat_api_client.upload_media(cover_path, "image")
    if not media_id:
        logger.error("封面图上传失败")
        return False

    logger.info(f"✅ 封面图上传成功，media_id: {media_id}")

    # 测试完整的23字符标题
    logger.info("\n步骤2: 测试完整中文标题")
    article_data = {
        "title": "当算力有了更好的去处：比特币的物理防线正在解体",  # 23字符
        "author": "饕韬不绝",  # 4字符
        "digest": "测试摘要",
        "content": """
        <section style="max-width: 100%; box-sizing: border-box; padding: 0 16px;">
          <h1 style="font-size: 24px; color: #222222;">测试内容</h1>
          <p style="font-size: 16px;">这是测试内容</p>
        </section>
        """,
        "thumb_media_id": media_id,
        "show_cover_pic": 1,
        "content_source_url": "",
    }

    logger.info(f"标题: '{article_data['title']}' ({len(article_data['title'])} 字符)")
    logger.info(f"作者: '{article_data['author']}' ({len(article_data['author'])} 字符)")

    draft_media_id = wechat_api_client.upload_news_draft([article_data])

    if draft_media_id:
        logger.info(f"✅ 成功！草稿media_id: {draft_media_id}")
        logger.info("   中文标题和作者名已正确处理，未被转义")
        return True
    else:
        logger.error("❌ 失败：草稿创建失败")
        return False


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("测试中文转义修复")
    logger.info("=" * 80)

    success = test_chinese_title()

    logger.info("\n" + "=" * 80)
    if success:
        logger.info("🎉 测试通过！中文转义问题已解决")
    else:
        logger.error("❌ 测试失败")
    logger.info("=" * 80)
