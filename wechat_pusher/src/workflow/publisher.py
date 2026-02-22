"""
微信公众号文章自动发布工作流
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

from src.ai.deepseek_client import deepseek_client
from src.ai.doubao_client import doubao_client
from src.chart.chart_generator import chart_generator
from src.converter.markdown_parser import MarkdownParser
from src.wechat.api_client import wechat_api_client
from src.utils.config import config
from src.utils.logger import get_logger
from src.services.chart_data_finder import get_chart_data_finder

logger = get_logger(__name__)


class ArticlePublisher:
    """文章自动发布器"""

    def __init__(self, fixed_author: str = None):
        """
        初始化发布器

        Args:
            fixed_author: 固定作者名称
        """
        self.fixed_author = fixed_author or config.article.default_author or "饕韬不绝"
        self.output_dir = Path(config.app.output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 初始化图表数据查找器（使用Gemini + Google Search）
        self.chart_data_finder = get_chart_data_finder()
        if self.chart_data_finder.is_available():
            logger.info("✅ 图表数据自动查找已启用（Gemini + Google Search）")
        else:
            logger.warning("⚠️  图表数据查找器不可用")

        # 初始化各个组件
        self.parser = MarkdownParser()

        logger.info(f"文章发布器初始化完成，固定作者: {self.fixed_author}")

    def parse_markdown(self, file_path: str) -> Tuple[str, str]:
        """
        解析Markdown文件

        Args:
            file_path: Markdown文件路径

        Returns:
            (title, content): 标题和内容
        """
        logger.info(f"解析Markdown文件: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取标题（第一个#标题）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # 移除标题行
            content = re.sub(r'^#\s+.+\n?', '', content, count=1)
        else:
            # 如果没有标题，使用文件名
            title = Path(file_path).stem
            logger.warning(f"未找到文章标题，使用文件名: {title}")

        logger.info(f"标题: {title}, 内容长度: {len(content)}字")
        return title, content

    def analyze_with_ai(self, title: str, content: str) -> Dict:
        """
        使用AI分析文章并生成资源

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            dict: 分析结果
                {
                    "summary": "摘要",
                    "cover_prompt": "封面提示词",
                    "placeholders": {
                        "charts": ["图表1描述", ...],
                        "images": ["插图1描述", ...]
                    },
                    "refined_content": "优化后的内容（包含占位符）"
                }
        """
        logger.info("开始AI分析文章...")

        result = {}

        # 1. 生成摘要
        logger.info("1/3 生成摘要...")
        result["summary"] = deepseek_client.generate_summary(content)
        logger.info(f"✅ 摘要生成成功: {len(result['summary'])}字符")

        # 2. 生成封面图提示词
        logger.info("2/3 生成封面图提示词...")
        prompts = deepseek_client.generate_image_prompts(content, title)
        result["cover_prompt"] = prompts.get("cover_prompts", [""])[0] if prompts.get("cover_prompts") else ""
        if result["cover_prompt"]:
            logger.info(f"✅ 封面图提示词生成成功")
        else:
            logger.warning("⚠️  封面图提示词生成失败")

        # 3. 优化内容并插入分类占位符
        logger.info("3/3 优化文章内容（包含分类占位符）...")
        result["refined_content"] = deepseek_client.refine_content(content)

        # 从优化后的内容中提取并分类占位符
        placeholders = deepseek_client.extract_image_placeholders(result["refined_content"])
        result["placeholders"] = placeholders

        logger.info(
            f"✅ 内容优化完成，提取到 {len(placeholders['charts'])} 个图表占位符 "
            f"和 {len(placeholders['images'])} 个插图占位符"
        )

        return result

    def generate_images(self, ai_result: Dict, article_id: str) -> Dict[str, List[str]]:
        """
        生成图片（根据占位符类型调用不同生成器）

        Args:
            ai_result: AI分析结果
                {
                    "cover_prompt": "封面提示词",
                    "placeholders": {
                        "charts": ["图表1描述", ...],
                        "images": ["插图1描述", ...]
                    }
                }
            article_id: 文章ID（用于命名文件）

        Returns:
            dict: 图片路径
                {
                    "covers": ["封面图1路径", ...],
                    "illustrations": ["插图1路径", ...],  # AI生成的概念图
                    "charts": ["图表路径", ...]          # Matplotlib生成的数据图表
                }
        """
        logger.info("开始生成图片...")

        result = {
            "covers": [],
            "illustrations": [],
            "charts": []
        }

        article_dir = self.output_dir / article_id
        article_dir.mkdir(exist_ok=True)

        placeholders = ai_result.get("placeholders", {"charts": [], "images": []})

        # 1. 生成封面图
        cover_prompt = ai_result.get("cover_prompt", "")
        if cover_prompt:
            logger.info("生成封面图...")
            cover_path = str(article_dir / "cover_1.png")
            generated_path = doubao_client.generate_cover_image(cover_prompt, cover_path)
            if generated_path:
                result["covers"].append(generated_path)
                logger.info(f"✅ 封面图生成成功")
            else:
                logger.error("❌ 封面图生成失败")
        else:
            logger.warning("⚠️  未提供封面图提示词，跳过封面图生成")

        # 2. 根据CHART占位符生成数据图表（使用Gemini查找数据）
        chart_descriptions = placeholders.get("charts", [])
        if chart_descriptions:
            logger.info(f"检测到 {len(chart_descriptions)} 个数据图表占位符")
            for i, desc in enumerate(chart_descriptions, 1):
                logger.info(f"处理图表{i}/{len(chart_descriptions)}...")
                logger.debug(f"  描述: {desc}")

                # 使用Gemini + Google Search自动查找数据
                chart_data_result = self.chart_data_finder.find_chart_data(desc)

                if chart_data_result and chart_data_result.get("found"):
                    # 成功找到数据，生成图表
                    chart_path = str(article_dir / f"chart_{i}.png")

                    # 构建图表配置
                    chart_config = {
                        "chart_type": chart_data_result.get("chart_type", "line"),
                        "title": chart_data_result.get("title", "数据图表"),
                        "data": {
                            "labels": chart_data_result.get("labels", []),
                            "values": chart_data_result.get("values", []),
                            "xlabel": chart_data_result.get("xlabel", ""),
                            "ylabel": chart_data_result.get("ylabel", "")
                        }
                    }

                    try:
                        generated_path = chart_generator.generate_chart(
                            chart_data=chart_config,
                            save_path=chart_path
                        )
                        if generated_path:
                            result["charts"].append(generated_path)
                            logger.info(f"✅ 图表{i}生成成功")
                            # 记录数据来源
                            source = chart_data_result.get("source", "N/A")
                            if source != "N/A":
                                logger.info(f"  数据来源: {source}")
                    except Exception as e:
                        logger.error(f"❌ 图表{i}生成失败: {e}")
                        import traceback
                        logger.debug(traceback.format_exc())
                else:
                    # 未找到数据，跳过此图表
                    reason = chart_data_result.get("reason", "未知原因") if chart_data_result else "查找器不可用"
                    logger.warning(f"⚠️  跳过图表{i}（未找到数据: {reason}）")
                    logger.info(f"   💡 提示：可以在占位符中明确提供数据，或简化描述")


        # 3. 根据IMAGE占位符生成概念插图（Doubao）
        image_descriptions = placeholders.get("images", [])
        if image_descriptions:
            logger.info(f"检测到 {len(image_descriptions)} 个概念插图占位符")
            for i, desc in enumerate(image_descriptions, 1):
                logger.info(f"生成插图{i}/{len(image_descriptions)}...")
                logger.debug(f"  描述: {desc}")

                illu_path = str(article_dir / f"illustration_{i}.png")
                generated_path = doubao_client.generate_illustration(desc, illu_path)
                if generated_path:
                    result["illustrations"].append(generated_path)
                    logger.info(f"✅ 插图{i}生成成功")
                else:
                    logger.error(f"❌ 插图{i}生成失败")

        logger.info(
            f"图片生成完成: {len(result['covers'])}封面 + "
            f"{len(result['illustrations'])}插图 + {len(result['charts'])}图表"
        )
        return result


    def upload_media_to_wechat(self, images: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """
        上传素材到微信

        Args:
            images: 图片路径字典

        Returns:
            dict: 素材信息字典
                {
                    "covers": [{"media_id": "xxx", "url": "https://..."}, ...],
                    "illustrations": [{"media_id": "xxx", "url": "https://..."}, ...],
                    "charts": [{"media_id": "xxx", "url": "https://..."}, ...]
                }
        """
        logger.info("开始上传素材到微信...")

        result = {
            "covers": [],
            "illustrations": [],
            "charts": []
        }

        # 上传封面图
        for i, cover_path in enumerate(images["covers"], 1):
            logger.info(f"上传封面图{i}/{len(images['covers'])}...")
            media_info = wechat_api_client.upload_media(cover_path, "image")
            if media_info:
                result["covers"].append(media_info)
                logger.info(f"✅ 封面图上传成功: {media_info['media_id']}")

        # 上传插图
        for i, illu_path in enumerate(images["illustrations"], 1):
            logger.info(f"上传插图{i}/{len(images['illustrations'])}...")
            media_info = wechat_api_client.upload_media(illu_path, "image")
            if media_info:
                result["illustrations"].append(media_info)
                logger.info(f"✅ 插图上传成功")

        # 上传图表
        for i, chart_path in enumerate(images["charts"], 1):
            logger.info(f"上传图表{i}/{len(images['charts'])}...")
            media_info = wechat_api_client.upload_media(chart_path, "image")
            if media_info:
                result["charts"].append(media_info)
                logger.info(f"✅ 图表上传成功")

        return result

    def convert_to_html(
        self,
        refined_content: str,
        summary: str,
        media_infos: Dict[str, List[Dict]]
    ) -> str:
        """
        转换为微信HTML并嵌入图片

        Args:
            refined_content: 优化后的Markdown内容
            summary: 文章摘要（由DeepSeek生成）
            media_infos: 图片素材信息字典（包含media_id和url）

        Returns:
            str: 微信规范HTML
        """
        logger.info("转换为微信HTML...")

        # 1. Markdown → HTML（新转换器）
        logger.info("1/2 Markdown转HTML（包含摘要）...")
        html_with_summary = self.parser.parse_content(
            content=refined_content,
            summary=summary
        )
        logger.info(f"✅ HTML生成成功，长度: {len(html_with_summary)}字符")

        # 2. 嵌入图片（使用真实URL）
        logger.info("2/2 嵌入图片...")
        html_with_images = self._embed_images(html_with_summary, media_infos)
        logger.info("✅ 图片嵌入完成")

        return html_with_images

    def _embed_images(self, html: str, media_infos: Dict[str, List[Dict]]) -> str:
        """
        精确替换图片占位符为真实img标签

        Args:
            html: 包含占位符的HTML内容
            media_infos: 素材信息字典（包含media_id和url）
                {
                    "illustrations": [{"media_id": "xxx", "url": "https://..."}, ...],
                    "charts": [{"media_id": "yyy", "url": "https://..."}, ...]
                }

        Returns:
            str: 替换后的HTML
        """
        import re

        result = html
        illustrations = media_infos.get("illustrations", [])
        charts = media_infos.get("charts", [])

        # 1. 替换CHART占位符 [[CHART:描述]]
        chart_pattern = r'\[\[CHART:[^\]]+\]\]'
        chart_placeholders = re.findall(chart_pattern, result)

        logger.info(f"替换 {len(chart_placeholders)} 个CHART占位符")

        if len(chart_placeholders) != len(charts):
            logger.warning(
                f"⚠️  CHART占位符数量({len(chart_placeholders)})与生成图表数量({len(charts)})不匹配"
            )

        for i, placeholder in enumerate(chart_placeholders):
            if i < len(charts):
                img_url = charts[i]['url']
                img_tag = f'''<section style="text-align: center; margin: 20px 0;">
  <img src="{img_url}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />
</section>'''

                result = result.replace(placeholder, img_tag, 1)
                logger.info(f"✅ 已替换CHART占位符{i+1}/{len(chart_placeholders)}")
            else:
                logger.warning(f"⚠️  CHART占位符{i+1}没有对应的图表，移除占位符")
                result = result.replace(placeholder, "", 1)

        # 2. 替换IMAGE占位符 [[IMAGE:描述]]
        image_pattern = r'\[\[IMAGE:[^\]]+\]\]'
        image_placeholders = re.findall(image_pattern, result)

        logger.info(f"替换 {len(image_placeholders)} 个IMAGE占位符")

        if len(image_placeholders) != len(illustrations):
            logger.warning(
                f"⚠️  IMAGE占位符数量({len(image_placeholders)})与生成插图数量({len(illustrations)})不匹配"
            )

        for i, placeholder in enumerate(image_placeholders):
            if i < len(illustrations):
                img_url = illustrations[i]['url']
                img_tag = f'''<section style="text-align: center; margin: 20px 0;">
  <img src="{img_url}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />
</section>'''

                result = result.replace(placeholder, img_tag, 1)
                logger.info(f"✅ 已替换IMAGE占位符{i+1}/{len(image_placeholders)}")
            else:
                logger.warning(f"⚠️  IMAGE占位符{i+1}没有对应的插图，移除占位符")
                result = result.replace(placeholder, "", 1)

        return result

    def publish_to_draft(
        self,
        title: str,
        html_content: str,
        summary: str,
        cover_media_id: str,
        author: str = None,
        enable_comments: bool = None,
        fans_only: bool = None
    ) -> Optional[str]:
        """
        发布到草稿箱

        Args:
            title: 文章标题
            html_content: HTML内容
            summary: 摘要
            cover_media_id: 封面图media_id
            author: 作者名称（可选，默认使用self.fixed_author）
            enable_comments: 是否开启评论（可选，默认使用配置）
            fans_only: 是否仅粉丝可评论（可选，默认使用配置）

        Returns:
            str: 草稿media_id
        """
        logger.info("发布到草稿箱...")

        # 使用传入的作者名或默认作者名
        final_author = author or self.fixed_author

        # 使用传入的评论设置或默认配置
        if enable_comments is None:
            enable_comments = config.article.enable_comments
        if fans_only is None:
            fans_only = config.article.fans_only

        # 构建文章数据
        article_data = {
            "title": title,
            "author": final_author,
            "digest": summary,
            "content": html_content,
            "thumb_media_id": cover_media_id,
            "show_cover_pic": 1,
            "content_source_url": "",
            # 留言设置
            "need_open_comment": 1 if enable_comments else 0,
            "only_fans_can_comment": 1 if fans_only else 0,
        }

        logger.info(f"留言设置: 开启评论={enable_comments}, 仅粉丝={fans_only}")

        draft_media_id = wechat_api_client.upload_news_draft([article_data])

        if draft_media_id:
            logger.info(f"✅ 草稿创建成功: {draft_media_id}")
            return draft_media_id
        else:
            logger.error("❌ 草稿创建失败")
            return None

    def publish(self, markdown_file: str) -> bool:
        """
        完整发布流程

        Args:
            markdown_file: Markdown文件路径

        Returns:
            bool: 是否成功
        """
        try:
            logger.info("=" * 80)
            logger.info(f"🚀 开始发布文章: {markdown_file}")
            logger.info("=" * 80)

            # 1. 解析Markdown
            title, content = self.parse_markdown(markdown_file)

            # 2. AI分析
            ai_result = self.analyze_with_ai(title, content)

            # 3. 生成图片和图表
            article_id = f"{int(time.time())}"
            images = self.generate_images(ai_result, article_id)

            # 检查是否生成了封面图
            if not images["covers"]:
                logger.error("❌ 未生成封面图，无法继续")
                return False

            # 4. 上传素材到微信
            media_ids = self.upload_media_to_wechat(images)

            # 5. 转换为HTML并嵌入图片（传入summary）
            html_content = self.convert_to_html(
                refined_content=ai_result["refined_content"],
                summary=ai_result["summary"],
                media_infos=media_ids
            )

            # 6. 发布到草稿箱
            draft_media_id = self.publish_to_draft(
                title=title,
                html_content=html_content,
                summary=ai_result["summary"],
                cover_media_id=media_ids["covers"][0]["media_id"],  # 使用第一个封面图的media_id
                author=self.fixed_author,
                enable_comments=config.article.enable_comments,
                fans_only=config.article.fans_only
            )

            if draft_media_id:
                logger.info("=" * 80)
                logger.info("🎉 文章发布成功！")
                logger.info(f"   草稿ID: {draft_media_id}")
                logger.info(f"   请在微信公众平台后台编辑和发布")
                logger.info("=" * 80)
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ 发布失败: {e}")
            import traceback
            traceback.print_exc()
            return False


# 创建全局实例
article_publisher = ArticlePublisher()

import time
