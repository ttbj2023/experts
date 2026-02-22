"""
测试获取微信素材列表
"""
from src.wechat.api_client import wechat_api_client
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


def test_get_materials():
    """获取图片素材列表"""

    logger.info("=" * 80)
    logger.info("获取微信素材列表")
    logger.info("=" * 80)

    result = wechat_api_client.get_material_list(material_type="image", offset=0, count=20)

    if result:
        logger.info(f"\n✅ 成功获取素材列表")
        logger.info(f"总素材数: {result['total_count']}")
        logger.info(f"本次返回: {result['item_count']}")
        logger.info("\n" + "=" * 80)
        logger.info("素材详情:")
        logger.info("=" * 80)

        for i, item in enumerate(result['item_list'], 1):
            media_id = item.get('media_id', 'N/A')
            name = item.get('name', 'N/A')
            url = item.get('url', 'N/A')
            update_time = item.get('update_time', 0)

            # 转换时间戳
            if update_time:
                dt = datetime.fromtimestamp(update_time)
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = 'N/A'

            logger.info(f"\n{i}. {name}")
            logger.info(f"   Media ID: {media_id}")
            logger.info(f"   URL: {url}")
            logger.info(f"   更新时间: {time_str}")

            # 构建微信图片URL格式
            if media_id != 'N/A':
                wechat_img_url = f"https://mmbiz.qpic.cn/mmbiz_jpg/{media_id}/0?wx_fmt=png"
                logger.info(f"   微信图片标签: <img src=\"{wechat_img_url}\" />")

        logger.info("\n" + "=" * 80)
        return True
    else:
        logger.error("❌ 获取素材列表失败")
        return False


if __name__ == "__main__":
    success = test_get_materials()

    if success:
        logger.info("\n🎉 测试完成！")
    else:
        logger.error("\n❌ 测试失败")
