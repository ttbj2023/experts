"""
配置管理模块
负责加载和管理所有环境变量配置
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


# 加载.env文件
load_dotenv()


class DeepSeekConfig(BaseSettings):
    """DeepSeek AI配置"""

    api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    model: str = Field(default="deepseek-v4-flash", alias="DEEPSEEK_MODEL")
    max_tokens: int = Field(default=4000, alias="DEEPSEEK_MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="DEEPSEEK_TEMPERATURE")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v:
            raise ValueError("DEEPSEEK_API_KEY环境变量未设置")
        return v


class DoubaoConfig(BaseSettings):
    """豆包AI配置"""

    api_key: str = Field(default="", alias="DOUBAO_API_KEY")
    base_url: str = Field(default="https://ark.cn-beijing.volces.com/api/v3", alias="DOUBAO_BASE_URL")
    model: str = Field(default="doubao-v3", alias="DOUBAO_MODEL")
    image_size: str = Field(default="1024x1024", alias="DOUBAO_IMAGE_SIZE")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v:
            raise ValueError("DOUBAO_API_KEY环境变量未设置")
        return v


class WeChatConfig(BaseSettings):
    """微信公众号配置"""

    appid: str = Field(default="", alias="WECHAT_APPID")
    secret: str = Field(default="", alias="WECHAT_SECRET")
    token_expire: int = Field(default=7200, alias="WECHAT_TOKEN_EXPIRE")

    @field_validator("appid", "secret")
    @classmethod
    def validate_wechat_credentials(cls, v: str) -> str:
        if not v:
            raise ValueError("微信APPID或SECRET环境变量未设置")
        return v


class AppConfig(BaseSettings):
    """应用配置"""

    output_dir: Path = Field(default=Path("./output"), alias="OUTPUT_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: Path = Field(default=Path("./logs/wechat_pusher.log"), alias="LOG_FILE")
    log_color: bool = Field(default=True, alias="LOG_COLOR")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是以下之一: {', '.join(valid_levels)}")
        return v.upper()

class APIConfig(BaseSettings):
    """API调用配置"""

    timeout: int = Field(default=30, alias="API_TIMEOUT")
    retry_times: int = Field(default=3, alias="API_RETRY_TIMES")
    retry_interval: int = Field(default=1, alias="API_RETRY_INTERVAL")
    enable_async: bool = Field(default=False, alias="ENABLE_ASYNC_API")


class ImageConfig(BaseSettings):
    """图片配置"""

    cover_width: int = Field(default=3840, alias="COVER_IMAGE_WIDTH")
    cover_height: int = Field(default=1632, alias="COVER_IMAGE_HEIGHT")
    cover_square_size: int = Field(default=3072, alias="COVER_SQUARE_SIZE")
    illustration_width: int = Field(default=3072, alias="ILLUSTRATION_WIDTH")
    illustration_height: int = Field(default=1898, alias="ILLUSTRATION_HEIGHT")
    guide_image_width: int = Field(default=3840, alias="GUIDE_IMAGE_WIDTH")
    guide_image_height: int = Field(default=2160, alias="GUIDE_IMAGE_HEIGHT")
    format: str = Field(default="png", alias="IMAGE_FORMAT")
    quality: int = Field(default=95, alias="IMAGE_QUALITY")


class ContentConfig(BaseSettings):
    """内容生成配置"""

    summary_length: int = Field(default=200, alias="SUMMARY_LENGTH")
    auto_generate_images: bool = Field(default=True, alias="AUTO_GENERATE_IMAGES")
    max_images_per_article: int = Field(default=10, alias="MAX_IMAGES_PER_ARTICLE")


class ArticleConfig(BaseSettings):
    """微信文章配置"""

    default_author: str = Field(default="饕韬不绝", alias="DEFAULT_AUTHOR")
    show_original: bool = Field(default=False, alias="SHOW_ORIGINAL")
    enable_comments: bool = Field(default=True, alias="ENABLE_COMMENTS")
    fans_only: bool = Field(default=False, alias="FANS_ONLY")


class WatermarkRemovalConfig(BaseSettings):
    """水印去除配置"""

    enabled: bool = Field(default=True, alias="WATERMARK_REMOVAL_ENABLED")
    watermark_remover_path: str = Field(
        default="/home/workspace/WatermarkRemover-AI",
        alias="WATERMARK_REMOVER_PATH"
    )


class Config:
    """全局配置管理器"""

    _instance: Optional["Config"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化所有配置"""
        if not hasattr(self, "_initialized"):
            self.deepseek = DeepSeekConfig()
            self.doubao = DoubaoConfig()
            self.wechat = WeChatConfig()
            self.app = AppConfig()
            self.api = APIConfig()
            self.image = ImageConfig()
            self.content = ContentConfig()
            self.article = ArticleConfig()
            self.watermark_removal = WatermarkRemovalConfig()

            # 创建必要的目录
            self._create_directories()

            self._initialized = True

    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.app.output_dir,
            self.app.output_dir / "html",
            self.app.output_dir / "images",
            self.app.log_file.parent,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def validate_all(self) -> bool:
        """验证所有必需的配置项"""
        try:
            # 验证DeepSeek配置
            self.deepseek.validate_api_key(self.deepseek.api_key)

            # 验证豆包配置
            self.doubao.validate_api_key(self.doubao.api_key)

            # 验证微信配置
            self.wechat.validate_wechat_credentials(self.wechat.appid)
            self.wechat.validate_wechat_credentials(self.wechat.secret)

            return True
        except ValueError as e:
            print(f"配置验证失败: {e}")
            return False

    def get_env_info(self) -> dict:
        """获取环境信息（用于调试）"""
        return {
            "deepseek_configured": bool(self.deepseek.api_key),
            "doubao_configured": bool(self.doubao.api_key),
            "wechat_configured": bool(self.wechat.appid and self.wechat.secret),
            "output_dir": str(self.app.output_dir),
            "log_level": self.app.log_level,
        }


# 全局配置实例
config = Config()
