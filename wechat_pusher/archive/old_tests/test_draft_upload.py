"""
测试微信公众号草稿上传
直接测试文章数据上传到微信草稿箱
"""
from src.wechat.api_client import wechat_api_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_draft_upload():
    """测试草稿上传功能"""

    # 先上传一个图片作为封面（即使不显示也需要thumb_media_id）
    logger.info("步骤1: 上传一张图片作为封面素材")
    import os
    from pathlib import Path

    # 查找已有的图片
    output_dir = Path("./output")
    cover_images = list(output_dir.glob("**/cover_1.png"))

    if cover_images:
        cover_path = str(cover_images[-1])
        logger.info(f"使用已有封面图: {cover_path}")
        media_id = wechat_api_client.upload_media(cover_path, "image")
        if not media_id:
            logger.error("❌ 封面图上传失败，无法继续测试")
            return False
        logger.info(f"✅ 封面图上传成功，media_id: {media_id}")
    else:
        logger.error("❌ 未找到封面图，请先运行完整发布流程生成图片")
        return False

    # 准备测试文章数据
    # 使用一个简短的标题来排除长度问题
    article_data = {
        "title": "测试文章",  # 只有4个字符
        "author": "作者",  # 使用简单的作者名（2个字符）
        "digest": "测试摘要",
        "content": """
        <section style="max-width: 100%; box-sizing: border-box; padding: 0 16px;">
          <h1 style="font-size: 24px; color: #222222; line-height: 1.3; text-align: center; margin: 24px 0 12px; font-weight: 700;">
            测试文章
          </h1>

          <p style="font-size: 16px; color: #333333; line-height: 1.75; margin: 16px 0;">
            这是测试内容。
          </p>
        </section>
        """,
        "thumb_media_id": media_id,
        "show_cover_pic": 0,  # 不显示封面图
        "content_source_url": "",
    }

    logger.info("=" * 80)
    logger.info("开始测试草稿上传...")
    logger.info("=" * 80)

    # 测试1: 不显示封面图的草稿（但必须有thumb_media_id）
    logger.info("\n测试1: 创建不显示封面图的草稿（show_cover_pic=0）")
    logger.info(f"标题: '{article_data['title']}'")
    logger.info(f"标题长度: {len(article_data['title'])} 字符")
    logger.info(f"作者: '{article_data['author']}' ({len(article_data['author'])} 字符)")

    draft_media_id = wechat_api_client.upload_news_draft([article_data])

    if draft_media_id:
        logger.info(f"✅ 测试1成功！草稿media_id: {draft_media_id}")
        logger.info(f"   请在微信公众平台后台查看草稿")
    else:
        logger.error("❌ 测试1失败：草稿创建失败")
        return False

    return True


def test_draft_with_cover():
    """测试带封面图的草稿上传"""

    # 先上传一张图片作为封面
    logger.info("\n" + "=" * 80)
    logger.info("测试2: 上传封面图并创建带封面的草稿")
    logger.info("=" * 80)

    # 使用之前生成的封面图路径（如果存在）
    import os
    from pathlib import Path

    # 查找最近生成的封面图
    output_dir = Path("./output")
    cover_images = list(output_dir.glob("**/cover_1.png"))

    if not cover_images:
        logger.warning("未找到封面图，跳过此测试")
        return True

    cover_path = str(cover_images[-1])  # 使用最新的封面图
    logger.info(f"使用封面图: {cover_path}")

    # 上传封面图
    media_id = wechat_api_client.upload_media(cover_path, "image")
    if not media_id:
        logger.error("❌ 封面图上传失败")
        return False

    logger.info(f"✅ 封面图上传成功，media_id: {media_id}")

    # 准备带封面图的文章数据
    article_data = {
        "title": "测试带封面",  # 5个字符
        "author": "作者",  # 使用简单的作者名
        "digest": "带封面的测试",
        "content": """
        <section style="max-width: 100%; box-sizing: border-box; padding: 0 16px;">
          <h1 style="font-size: 24px; color: #222222; line-height: 1.3; text-align: center; margin: 24px 0 12px; font-weight: 700;">
            测试带封面
          </h1>

          <p style="font-size: 16px; color: #333333; line-height: 1.75; margin: 16px 0;">
            这是带封面图的测试文章内容。
          </p>
        </section>
        """,
        "thumb_media_id": media_id,
        "show_cover_pic": 1,  # 显示封面图
        "content_source_url": "",
    }

    logger.info(f"标题: '{article_data['title']}'")
    logger.info(f"标题长度: {len(article_data['title'])} 字符")

    # 创建草稿
    draft_media_id = wechat_api_client.upload_news_draft([article_data])

    if draft_media_id:
        logger.info(f"✅ 测试2成功！草稿media_id: {draft_media_id}")
        return True
    else:
        logger.error("❌ 测试2失败：带封面图的草稿创建失败")
        return False


if __name__ == "__main__":
    # 测试1: 不带封面图的草稿
    success1 = test_draft_upload()

    # 测试2: 带封面图的草稿
    success2 = test_draft_with_cover()

    # 总结
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"测试1（不带封面）: {'✅ 通过' if success1 else '❌ 失败'}")
    logger.info(f"测试2（带封面）: {'✅ 通过' if success2 else '❌ 失败'}")

    if success1 and success2:
        logger.info("\n🎉 所有测试通过！草稿上传功能正常")
    else:
        logger.error("\n⚠️ 部分测试失败，请检查日志")
