"""
水印去除工具

集成 WatermarkRemover-AI 功能，用于去除豆包生成的图片中的水印
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class WatermarkRemover:
    """水印去除工具"""

    def __init__(self):
        """
        初始化水印去除工具
        """
        # 从配置读取是否启用
        self.enabled = config.watermark_removal.enabled

        if not self.enabled:
            logger.info("⚠️  水印去除功能已禁用（通过配置）")
            self.available = False
            return

        # 从配置读取路径
        watermark_remover_path = config.watermark_removal.watermark_remover_path
        self.watermark_remover_path = Path(watermark_remover_path)
        self.remwm_script = self.watermark_remover_path / "remwm.py"
        self.venv_python = self.watermark_remover_path / ".venv" / "bin" / "python"

        # 检查 WatermarkRemover-AI 是否存在
        if not self.remwm_script.exists():
            logger.warning(f"⚠️  WatermarkRemover-AI 未找到: {self.remwm_script}")
            logger.warning("⚠️  水印去除功能将不可用")
            self.available = False
        elif not self.venv_python.exists():
            logger.warning(f"⚠️  WatermarkRemover-AI 虚拟环境未找到: {self.venv_python}")
            logger.warning("⚠️  水印去除功能将不可用")
            self.available = False
        else:
            self.available = True
            logger.info(f"✅ WatermarkRemover-AI 已找到: {self.remwm_script}")
            logger.info(f"✅ 使用虚拟环境: {self.venv_python}")
            logger.info(f"✅ 水印去除功能已启用")

    def remove_watermark(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        overwrite: bool = True
    ) -> Optional[str]:
        """
        去除图片水印

        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径（如果为None，则覆盖原文件）
            overwrite: 是否覆盖原文件

        Returns:
            处理后的图片路径，如果处理失败则返回None
        """
        if not self.available:
            logger.warning("水印去除功能不可用，跳过处理")
            return None

        input_path = Path(input_path)

        # 如果没有指定输出路径，使用临时文件
        if output_path is None:
            if overwrite:
                # 使用临时文件，成功后再替换原文件
                with tempfile.NamedTemporaryFile(suffix=input_path.suffix, delete=False) as tmp:
                    output_path = tmp.name
                final_output = str(input_path)
            else:
                output_path = str(input_path).replace(input_path.suffix, f"_no_wm{input_path.suffix}")
                final_output = output_path
        else:
            final_output = output_path

        output_dir = str(Path(output_path).parent)

        try:
            logger.info(f"开始去除水印: {input_path.name}")

            # 构建命令（使用虚拟环境的 Python）
            cmd = [
                str(self.venv_python),
                str(self.remwm_script),
                str(input_path),
                output_dir,
                "--overwrite"
            ]

            # 执行命令
            result = subprocess.run(
                cmd,
                cwd=str(self.watermark_remover_path),
                capture_output=True,
                text=True,
                timeout=120  # 2分钟超时
            )

            if result.returncode == 0:
                # 查找生成的文件
                output_file = Path(output_dir) / input_path.name

                if output_file.exists():
                    # 如果需要覆盖原文件
                    if overwrite and str(output_file) != str(input_path):
                        import shutil
                        shutil.move(str(output_file), final_output)

                    logger.info(f"✅ 水印去除完成: {final_output}")
                    return final_output
                else:
                    logger.warning(f"⚠️  输出文件未找到: {output_file}")
                    return None
            else:
                logger.error(f"❌ 水印去除失败: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"❌ 水印去除超时")
            return None
        except Exception as e:
            logger.error(f"❌ 水印去除异常: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None


# 创建全局实例
watermark_remover = WatermarkRemover()
