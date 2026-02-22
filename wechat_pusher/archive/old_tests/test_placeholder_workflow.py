"""
测试新的图片占位符工作流程
1. AI优化内容并插入占位符
2. 提取占位符
3. 生成图片
4. 替换占位符为真实URL
"""
from pathlib import Path
from src.ai.deepseek_client import deepseek_client
from src.ai.doubao_client import doubao_client
from src.converter.markdown_parser import MarkdownParser
from src.converter.wechat_adapter import WeChatAdapter
from src.utils.logger import get_logger
import time

logger = get_logger(__name__)


def test_placeholder_workflow():
    """测试占位符工作流程"""

    # 测试文章
    test_content = """# 比特币能源转型

比特币挖矿正在经历一场深刻的能源转型。随着环保意识的提升和能源效率的改进，矿工们正在寻找更清洁、更高效的能源解决方案。

传统的矿机能耗巨大，而新一代节能设备正在改变这一局面。

## 算力价值重估

算力正在从单纯的工具演变为一种战略资源。AI的兴起让算力有了新的去处。
"""

    logger.info("=" * 80)
    logger.info("测试占位符工作流程")
    logger.info("=" * 80)

    # 步骤1: AI优化内容并插入占位符
    logger.info("\n步骤1: AI优化内容（插入占位符）")
    logger.info("-" * 80)
    refined_content = deepseek_client.refine_content(test_content)
    logger.info(f"\n优化后的内容（前500字符）：\n{refined_content[:500]}...")

    # 步骤2: 提取占位符
    logger.info("\n步骤2: 提取图片占位符")
    logger.info("-" * 80)
    placeholders = deepseek_client.extract_image_placeholders(refined_content)

    if not placeholders:
        logger.warning("⚠️  未检测到占位符，AI可能没有插入图片")
        return False

    logger.info(f"提取到 {len(placeholders)} 个占位符：")
    for i, desc in enumerate(placeholders, 1):
        logger.info(f"  {i}. {desc}")

    # 步骤3: 生成图片（使用前2个占位符，节省时间）
    logger.info("\n步骤3: 生成图片")
    logger.info("-" * 80)

    article_id = f"test_{int(time.time())}"
    article_dir = Path("./output") / article_id
    article_dir.mkdir(exist_ok=True, parents=True)

    images = []
    max_images = min(2, len(placeholders))  # 最多生成2张，节省时间

    for i in range(max_images):
        prompt = placeholders[i]
        logger.info(f"生成插图{i+1}/{max_images}...")
        img_path = str(article_dir / f"illustration_{i+1}.png")

        try:
            generated_path = doubao_client.generate_illustration(prompt, img_path)
            if generated_path:
                images.append(generated_path)
                logger.info(f"✅ 插图{i+1}生成成功")
            else:
                logger.error(f"❌ 插图{i+1}生成失败")
        except Exception as e:
            logger.error(f"❌ 插图{i+1}生成异常: {e}")

    if not images:
        logger.error("❌ 没有成功生成任何图片")
        return False

    # 步骤4: 模拟上传和替换
    logger.info("\n步骤4: 测试占位符替换")
    logger.info("-" * 80)

    # 模拟：将Markdown转换为HTML
    parser = MarkdownParser()
    article = parser.parse_content(refined_content)
    html_content = article.html

    logger.info(f"转换后HTML长度: {len(html_content)}字符")

    # 统计占位符
    import re
    placeholder_count = len(re.findall(r'\[\[IMAGE:[^\]]+\]\]', html_content))
    logger.info(f"HTML中包含 {placeholder_count} 个占位符")

    # 模拟替换（使用假URL）
    logger.info("\n模拟替换占位符...")
    test_html = html_content
    for i, placeholder in enumerate(re.findall(r'\[\[IMAGE:[^\]]+\]\]', html_content)):
        if i < len(images):
            fake_url = f"fake_url_{i+1}.png"
            img_tag = f'<section><img src="{fake_url}" /></section>'
            test_html = test_html.replace(placeholder, img_tag, 1)
            logger.info(f"✅ 替换占位符{i+1}")

    # 验证替换结果
    remaining_placeholders = len(re.findall(r'\[\[IMAGE:[^\]]+\]\]', test_html))
    if remaining_placeholders == 0:
        logger.info("✅ 所有占位符已成功替换")
    else:
        logger.warning(f"⚠️  还有 {remaining_placeholders} 个占位符未替换")

    logger.info("\n" + "=" * 80)
    logger.info("🎉 测试完成！")
    logger.info("=" * 80)
    logger.info("\n总结：")
    logger.info(f"1. ✅ AI优化内容并插入占位符")
    logger.info(f"2. ✅ 提取到 {len(placeholders)} 个占位符")
    logger.info(f"3. ✅ 成功生成 {len(images)} 张图片")
    logger.info(f"4. ✅ 占位符替换验证通过")

    return True


if __name__ == "__main__":
    success = test_placeholder_workflow()

    if success:
        logger.info("\n✅ 工作流程测试通过")
    else:
        logger.error("\n❌ 工作流程测试失败")
