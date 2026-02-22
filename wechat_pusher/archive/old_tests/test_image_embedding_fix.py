"""
测试修复后的图片嵌入功能
使用真实URL，智能分段插入图片
"""
from pathlib import Path
from src.wechat.api_client import wechat_api_client
from src.converter.markdown_parser import MarkdownParser
from src.converter.html_builder import HTMLBuilder
from src.converter.wechat_adapter import WeChatAdapter
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_image_embedding():
    """测试图片嵌入功能"""

    logger.info("=" * 80)
    logger.info("测试修复后的图片嵌入功能")
    logger.info("=" * 80)

    # 1. 获取最新的封面图和插图素材
    result = wechat_api_client.get_material_list(material_type="image", offset=0, count=5)

    if not result or len(result['item_list']) < 2:
        logger.error("素材不足，无法测试")
        return False

    # 提取素材信息
    items = result['item_list']
    cover = items[0]  # 封面图
    illustration1 = items[1]  # 插图1

    logger.info(f"\n使用素材:")
    logger.info(f"封面: {cover['name']}")
    logger.info(f"插图1: {illustration1['name']}")

    # 2. 准备测试内容（多段落）
    test_markdown = """# 测试文章：智能图片嵌入

这是第一段内容，用于测试图片智能插入功能。

这是第二段内容，图片应该插入到段落之间，而不是全部追加到末尾。

这是第三段内容。

这是第四段内容。

这是第五段内容。

这是第六段内容。

这是第七段内容。

这是第八段内容。
"""

    # 3. 转换为HTML
    parser = MarkdownParser()
    builder = HTMLBuilder()
    adapter = WeChatAdapter()

    article = parser.parse_content(test_markdown)
    raw_html = article.html

    logger.info(f"\n原始HTML:\n{raw_html[:200]}...")

    # 4. 手动嵌入图片（使用真实URL）
    media_infos = {
        "covers": [cover],
        "illustrations": [illustration1],
        "charts": []
    }

    # 模拟_embed_images逻辑
    import re

    html = raw_html
    paragraphs = re.split(r'(</p>)', html)
    total_paragraphs = len([p for p in paragraphs if '<p>' in p or p.strip()])
    illustrations = media_infos.get("illustrations", [])

    logger.info(f"\n总段落数: {total_paragraphs}")
    logger.info(f"插图数量: {len(illustrations)}")

    if total_paragraphs > 0 and illustrations:
        interval = max(1, total_paragraphs // len(illustrations))
        logger.info(f"每隔{interval}段插入一张图片")

        img_index = 0
        inserted_count = 0

        for i in range(len(paragraphs)):
            if paragraphs[i] == '</p>' and inserted_count < len(illustrations):
                if (i // 2 + 1) % interval == 0 and img_index < len(illustrations):
                    img_url = illustrations[img_index]['url']
                    img_tag = f'''
<section style="text-align: center; margin: 20px 0;">
  <img src="{img_url}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />
</section>'''
                    paragraphs[i] += img_tag
                    logger.info(f"✅ 在第{i//2 + 1}段后插入插图{img_index + 1}")
                    img_index += 1
                    inserted_count += 1

    html_with_images = ''.join(paragraphs)

    # 5. 微信适配
    wechat_html = adapter.adapt(html_with_images)

    # 6. 创建测试草稿
    article_data = {
        "title": "测试图片嵌入修复",
        "author": "测试",
        "digest": "测试真实URL和智能分段插入",
        "content": wechat_html,
        "thumb_media_id": cover['media_id'],
        "show_cover_pic": 0,
        "content_source_url": "",
    }

    logger.info("\n" + "=" * 80)
    logger.info("创建测试草稿...")
    logger.info("=" * 80)

    draft_id = wechat_api_client.upload_news_draft([article_data])

    if draft_id:
        logger.info(f"✅ 草稿创建成功: {draft_id}")
        logger.info("\n请在微信公众平台查看:")
        logger.info("1. 图片是否正常显示（使用真实URL）")
        logger.info("2. 图片是否智能分布在段落之间")
        logger.info("3. 图片是否居中显示")
        return True
    else:
        logger.error("❌ 草稿创建失败")
        return False


if __name__ == "__main__":
    success = test_image_embedding()

    if success:
        logger.info("\n🎉 测试完成！")
    else:
        logger.error("\n❌ 测试失败")
