"""Claude 文档处理专家

基于 Claude Code CLI 的文档处理专家工具。
支持文档格式转换、图片识别、内容增强等功能。
"""

from pathlib import Path


class ClaudeDocProcessorExpert:
    """Claude 文档处理专家

    封装文档处理专家的工具接口和元数据。
    """

    def __init__(self, experts_root: Path):
        """初始化专家

        Args:
            experts_root: 专家工具根目录（包含 .claude/ 等）
        """
        self.experts_root = experts_root
        self.name = "claude-doc-processor"
        self.description = "文档格式转换和内容增强专家工具"

    def get_config(self) -> dict:
        """获取专家配置

        Returns:
            专家配置字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "expert_path": str(self.experts_root),
            "supported_formats": ["md", "pdf", "docx", "html", "txt"],
            "capabilities": [
                "format_conversion",
                "image_recognition",
                "content_enhancement",
                "data_extraction"
            ]
        }


__all__ = ["ClaudeDocProcessorExpert"]
