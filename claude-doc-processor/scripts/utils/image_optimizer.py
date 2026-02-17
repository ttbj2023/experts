#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Optimizer

使用pngquant压缩PNG图片以减小文件大小
支持批量处理图片目录
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageOptimizer:
    """图片压缩优化器"""

    def __init__(self, quality: int = 85):
        """
        初始化图片优化器

        Args:
            quality: 压缩质量 (1-100)，默认85
        """
        self.quality = quality
        self.stats = {
            'total': 0,
            'optimized': 0,
            'failed': 0,
            'original_size': 0,
            'optimized_size': 0,
            'saved_bytes': 0
        }

        # 检查pngquant是否可用
        self.pngquant_available = self._check_pngquant()

    def _check_pngquant(self) -> bool:
        """检查pngquant是否可用"""
        try:
            result = subprocess.run(['which', 'pngquant'],
                                  capture_output=True,
                                  text=True)
            if result.returncode == 0:
                logger.info(f"找到pngquant: {result.stdout.strip()}")
                return True
            else:
                logger.warning("未找到pngquant，图片压缩功能将不可用")
                return False
        except Exception as e:
            logger.error(f"检查pngquant失败: {str(e)}")
            return False

    def optimize_image(self, image_path: str) -> Tuple[bool, int, int]:
        """
        压缩单个PNG图片

        Args:
            image_path: 图片文件路径

        Returns:
            (success, original_size, optimized_size): 是否成功、原始大小、压缩后大小
        """
        if not self.pngquant_available:
            logger.warning(f"pngquant不可用，跳过图片压缩: {image_path}")
            return False, 0, 0

        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return False, 0, 0

        # 获取原始文件大小
        try:
            original_size = os.path.getsize(image_path)
        except Exception as e:
            logger.error(f"无法获取文件大小: {image_path}, {str(e)}")
            return False, 0, 0

        self.stats['total'] += 1

        try:
            # 构建pngquant命令
            # --quality: 质量 (min-max)
            # --ext: 输出文件扩展名
            # --force: 覆盖已存在的文件
            quality_min = max(1, self.quality - 20)
            quality_max = min(100, self.quality + 5)

            cmd = [
                'pngquant',
                '--quality', f'{quality_min}-{quality_max}',
                '--ext', '.png',
                '--force',
                image_path
            ]

            # 执行压缩
            result = subprocess.run(cmd,
                                  capture_output=True,
                                  text=True)

            if result.returncode == 0:
                # 获取压缩后文件大小
                optimized_size = os.path.getsize(image_path)
                saved_bytes = original_size - optimized_size
                saved_percent = (saved_bytes / original_size * 100) if original_size > 0 else 0

                self.stats['optimized'] += 1
                self.stats['original_size'] += original_size
                self.stats['optimized_size'] += optimized_size
                self.stats['saved_bytes'] += saved_bytes

                logger.info(f"图片压缩成功: {image_path}")
                logger.debug(f"  原始大小: {original_size:,} bytes")
                logger.debug(f"  压缩后: {optimized_size:,} bytes")
                logger.debug(f"  节省: {saved_bytes:,} bytes ({saved_percent:.1f}%)")

                return True, original_size, optimized_size
            else:
                self.stats['failed'] += 1
                logger.warning(f"图片压缩失败: {image_path}")
                logger.debug(f"  错误信息: {result.stderr}")
                return False, original_size, original_size

        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"图片压缩异常: {image_path}, {str(e)}")
            return False, original_size, original_size

    def optimize_directory(self, directory: str, recursive: bool = False) -> dict:
        """
        批量压缩目录下的所有PNG图片

        Args:
            directory: 图片目录路径
            recursive: 是否递归处理子目录

        Returns:
            统计信息字典
        """
        if not os.path.exists(directory):
            logger.error(f"目录不存在: {directory}")
            return self.stats

        # 查找所有PNG文件
        if recursive:
            pattern = "**/*.png"
        else:
            pattern = "*.png"

        png_files = list(Path(directory).glob(pattern))

        if not png_files:
            logger.warning(f"未找到PNG文件: {directory}")
            return self.stats

        logger.info(f"开始批量压缩图片，共 {len(png_files)} 个文件")

        for i, png_file in enumerate(png_files, 1):
            logger.info(f"[{i}/{len(png_files)}] 处理: {png_file.name}")
            self.optimize_image(str(png_file))

        # 生成统计报告
        total_saved_percent = (self.stats['saved_bytes'] / self.stats['original_size'] * 100) \
            if self.stats['original_size'] > 0 else 0

        logger.info("=" * 60)
        logger.info("批量压缩完成")
        logger.info(f"  总文件数: {self.stats['total']}")
        logger.info(f"  成功压缩: {self.stats['optimized']}")
        logger.info(f"  压缩失败: {self.stats['failed']}")
        logger.info(f"  原始大小: {self.stats['original_size']:,} bytes ({self.stats['original_size']/1024/1024:.2f} MB)")
        logger.info(f"  压缩后: {self.stats['optimized_size']:,} bytes ({self.stats['optimized_size']/1024/1024:.2f} MB)")
        logger.info(f"  节省空间: {self.stats['saved_bytes']:,} bytes ({total_saved_percent:.1f}%)")
        logger.info("=" * 60)

        return self.stats

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total': 0,
            'optimized': 0,
            'failed': 0,
            'original_size': 0,
            'optimized_size': 0,
            'saved_bytes': 0
        }

    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()


def main():
    """测试图片压缩功能"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 image_optimizer.py <图片文件或目录> [递归:True/False]")
        sys.exit(1)

    input_path = sys.argv[1]
    recursive = len(sys.argv) > 2 and sys.argv[2].lower() == 'true'

    optimizer = ImageOptimizer(quality=85)

    if os.path.isfile(input_path):
        # 单个文件
        success, orig_size, opt_size = optimizer.optimize_image(input_path)
        if success:
            saved = orig_size - opt_size
            print(f"压缩成功！节省: {saved:,} bytes ({saved/orig_size*100:.1f}%)")
        else:
            print("压缩失败")
    elif os.path.isdir(input_path):
        # 目录
        stats = optimizer.optimize_directory(input_path, recursive=recursive)
        print(stats)
    else:
        print(f"错误: 路径不存在: {input_path}")


if __name__ == "__main__":
    main()
