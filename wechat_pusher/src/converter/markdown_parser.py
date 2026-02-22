"""
Markdown解析器
负责解析Markdown文件并转换为微信公众号HTML
"""
import re
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger
from src.converter.wechat_markdown_converter import convert_markdown_content_to_wechat

logger = get_logger(__name__)


class MarkdownParser:
    """Markdown解析器（使用新转换器）"""

    def __init__(self):
        """初始化解析器"""
        pass

    def parse_file(self, file_path: str) -> str:
        """
        解析Markdown文件并转换为HTML

        Args:
            file_path: Markdown文件路径

        Returns:
            str: 微信公众号HTML
        """
        logger.info(f"开始解析Markdown文件: {file_path}")

        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 读取文件内容
            content = path.read_text(encoding="utf-8")

            # 解析内容
            html = self.parse_content(content)

            logger.info(f"解析完成: HTML长度={len(html)}")
            return html

        except Exception as e:
            logger.error(f"解析Markdown文件失败: {e}")
            raise

    def parse_content(
        self,
        content: str,
        title: str = None,
        summary: str = None
    ) -> str:
        """
        解析Markdown内容并转换为HTML

        Args:
            content: Markdown文本内容
            title: 文章标题（可选）
            summary: 文章摘要（可选）

        Returns:
            str: 微信公众号HTML
        """
        # 调用新转换器
        html = convert_markdown_content_to_wechat(
            markdown_content=content,
            title=title,
            summary=summary
        )

        return html
