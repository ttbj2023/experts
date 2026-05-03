"""
豆包AI客户端
用于生成封面图和插图
"""
import requests
from pathlib import Path
from typing import Optional
from PIL import Image
import io

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DoubaoClient:
    """豆包AI客户端（图片生成）"""

    def __init__(self):
        """初始化客户端"""
        self.api_key = config.doubao.api_key
        self.base_url = config.doubao.base_url
        self.model = config.doubao.model
        self.image_size = config.doubao.image_size

        logger.info(f"豆包客户端初始化完成 - 模型: {self.model}")

    def generate_image(
        self,
        prompt: str,
        save_path: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> Optional[str]:
        """
        生成图片

        Args:
            prompt: 图片描述提示词
            save_path: 保存路径（可选）
            width: 图片宽度
            height: 图片高度

        Returns:
            str: 图片保存路径，失败返回None
        """
        logger.info(f"开始生成图片: {prompt[:50]}...")

        try:
            # 使用火山引擎官方的图像生成API (OpenAI兼容格式)
            url = f"{self.base_url}/images/generations"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "prompt": prompt,
                "size": f"{width}x{height}",
                "n": 1,
            }

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求数据: {data}")

            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()

            result = response.json()

            logger.info(f"API响应成功，图片生成完成")

            # 解析响应获取图片URL
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]

                # 如果返回的是URL
                if "url" in image_data:
                    image_url = image_data["url"]
                    logger.info(f"图片URL: {image_url}")
                    return self._download_image(image_url, save_path)

                # 如果返回的是base64
                elif "b64_json" in image_data:
                    logger.info("收到base64格式图片")
                    return self._save_base64_image(
                        image_data["b64_json"], save_path
                    )

            logger.error("API响应中没有图片数据")
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {e}")
            if e.response:
                logger.error(f"状态码: {e.response.status_code}")
                logger.error(f"响应内容: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return None

    def generate_cover_image(self, prompt: str, save_path: Optional[str] = None) -> Optional[str]:
        """
        生成封面图（2.5:1比例）

        Args:
            prompt: 图片描述
            save_path: 保存路径

        Returns:
            str: 图片保存路径
        """
        width = config.image.cover_width
        height = config.image.cover_height

        # 优化后的提示词：强调纯视觉符号，去除干扰信息
        full_prompt = f"{prompt}, high quality, professional, clean design, visual symbols only, no text, no words, no letters, no numbers, no labels, no titles, minimal illustration, abstract concept, 2.5:1 aspect ratio"

        return self.generate_image(full_prompt, save_path, width, height)

    def generate_illustration(self, prompt: str, save_path: Optional[str] = None) -> Optional[str]:
        """
        生成插图（黄金比例）

        Args:
            prompt: 图片描述
            save_path: 保存路径

        Returns:
            str: 图片保存路径
        """
        # 黄金比例1.618:1（符合Seedream 4.5要求）
        width = config.image.illustration_width
        height = config.image.illustration_height

        # 添加约束：纯视觉符号，不包含任何文字
        full_prompt = f"{prompt}, visual symbols only, no text, no words, no letters, no numbers, no labels, no titles"

        return self.generate_image(full_prompt, save_path, width, height)

    def _download_image(self, url: str, save_path: Optional[str] = None) -> str:
        """
        下载图片

        Args:
            url: 图片URL
            save_path: 保存路径

        Returns:
            str: 保存路径
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # 如果没有指定保存路径，使用默认路径
            if not save_path:
                output_dir = Path(config.app.output_dir) / "images"
                output_dir.mkdir(parents=True, exist_ok=True)
                save_path = str(output_dir / f"image_{id(url)}.png")

            # 保存图片
            with open(save_path, "wb") as f:
                f.write(response.content)

            logger.info(f"图片已保存: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"图片下载失败: {e}")
            raise

    def _save_base64_image(self, b64_data: str, save_path: Optional[str] = None) -> str:
        """
        保存base64格式的图片

        Args:
            b64_data: base64编码的图片数据
            save_path: 保存路径

        Returns:
            str: 保存路径
        """
        try:
            import base64

            # 解码base64
            image_data = base64.b64decode(b64_data)

            # 如果没有指定保存路径，使用默认路径
            if not save_path:
                output_dir = Path(config.app.output_dir) / "images"
                output_dir.mkdir(parents=True, exist_ok=True)
                save_path = str(output_dir / f"image_{id(b64_data)}.png")

            # 保存图片
            with open(save_path, "wb") as f:
                f.write(image_data)

            logger.info(f"图片已保存: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"base64图片保存失败: {e}")
            raise

    def resize_image(
        self, image_path: str, target_width: int, target_height: int
    ) -> str:
        """
        调整图片尺寸

        Args:
            image_path: 原始图片路径
            target_width: 目标宽度
            target_height: 目标高度

        Returns:
            str: 处理后的图片路径
        """
        try:
            img = Image.open(image_path)

            # 调整尺寸（保持宽高比）
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

            # 保存
            output_path = image_path.replace(".", "_resized.")
            img.save(output_path, quality=config.image.quality)

            logger.info(f"图片已调整尺寸: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"图片尺寸调整失败: {e}")
            return image_path


# 创建全局实例
doubao_client = DoubaoClient()
