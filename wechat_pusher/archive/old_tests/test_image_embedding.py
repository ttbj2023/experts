"""
测试图片嵌入方式
比较3种不同的图片引用方式
"""
from src.wechat.api_client import wechat_api_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_image_embedding_methods():
    """测试3种图片嵌入方式"""

    # 获取最新的封面图
    result = wechat_api_client.get_material_list(material_type="image", offset=0, count=1)

    if not result or not result['item_list']:
        logger.error("无法获取素材")
        return False

    item = result['item_list'][0]
    media_id = item['media_id']
    real_url = item['url']  # API返回的真实URL
    name = item['name']

    logger.info("=" * 80)
    logger.info(f"测试图片: {name}")
    logger.info("=" * 80)
    logger.info(f"Media ID: {media_id}")
    logger.info(f"真实URL: {real_url}")

    # 构造3种不同的引用方式
    method1_url = f"https://mmbiz.qpic.cn/mmbiz_jpg/{media_id}/0?wx_fmt=png"

    logger.info("\n" + "=" * 80)
    logger.info("方法1: 使用media_id构造URL（当前方式）")
    logger.info("=" * 80)
    logger.info(f"URL: {method1_url}")

    logger.info("\n" + "=" * 80)
    logger.info("方法2: 使用API返回的真实URL")
    logger.info("=" * 80)
    logger.info(f"URL: {real_url}")

    logger.info("\n" + "=" * 80)
    logger.info("方法3: 直接在HTML中使用wx_fmt标签（推荐）")
    logger.info("=" * 80)
    logger.info("可能需要查询微信文档获取正确格式")

    # 创建测试草稿，比较3种方式
    test_articles = []

    # 方法1: media_id构造
    test_articles.append({
        "title": "测试1-media_id构造",
        "author": "测试",
        "digest": "测试方法1",
        "content": f'<section><h2>方法1测试</h2><p>使用media_id构造URL</p><img src="{method1_url}" /></section>',
        "thumb_media_id": media_id,
        "show_cover_pic": 0,
        "content_source_url": "",
    })

    # 方法2: 真实URL
    test_articles.append({
        "title": "测试2-真实URL",
        "author": "测试",
        "digest": "测试方法2",
        "content": f'<section><h2>方法2测试</h2><p>使用API返回的真实URL</p><img src="{real_url}" /></section>',
        "thumb_media_id": media_id,
        "show_cover_pic": 0,
        "content_source_url": "",
    })

    # 逐个测试
    for i, article in enumerate(test_articles, 1):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"创建测试草稿{i}: {article['title']}")
        logger.info('=' * 80)

        draft_id = wechat_api_client.upload_news_draft([article])

        if draft_id:
            logger.info(f"✅ 草稿{i}创建成功: {draft_id}")
            logger.info(f"   请在微信公众平台查看图片是否正常显示")
        else:
            logger.error(f"❌ 草稿{i}创建失败")

    return True


if __name__ == "__main__":
    success = test_image_embedding_methods()

    if success:
        logger.info("\n🎉 测试完成！请在微信公众平台查看草稿，对比3种方法的显示效果")
    else:
        logger.error("\n❌ 测试失败")
