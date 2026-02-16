#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片 Base64 编码器
==================

将图片文件转换为 base64 编码的 data URI，用于内嵌到 Word 兼容的 HTML 中。

功能：
- 支持 PNG、JPEG、JPG 格式
- 自动检测图片类型
- 可选图片压缩
- 生成 Word 完全兼容的 data URI

作者：Claude Code
版本：v1.0
"""

import os
import base64
from typing import Optional, Tuple
from PIL import Image
import io


class ImageBase64Encoder:
    """图片 Base64 编码器"""

    # 支持的图片格式
    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg']

    # MIME 类型映射
    MIME_TYPES = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg'
    }

    def __init__(self, max_size: Optional[int] = None, quality: int = 85):
        """
        初始化编码器

        Args:
            max_size: 图片最大尺寸（宽或高），超过会等比压缩
            quality: JPEG 压缩质量（1-100），仅对 JPEG 有效
        """
        self.max_size = max_size
        self.quality = quality

    def encode_image(self, image_path: str) -> str:
        """
        将图片文件编码为 base64 data URI

        Args:
            image_path: 图片文件路径

        Returns:
            base64 data URI 字符串，例如：'data:image/png;base64,iVBORw0KG...'

        Raises:
            FileNotFoundError: 图片文件不存在
            ValueError: 不支持的图片格式
        """
        # 验证文件存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 检查文件扩展名
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的图片格式: {ext}，支持的格式: {self.SUPPORTED_FORMATS}")

        # 读取图片数据
        if self.max_size is not None:
            # 需要压缩图片
            image_data = self._compress_image(image_path)
        else:
            # 直接读取
            with open(image_path, 'rb') as f:
                image_data = f.read()

        # Base64 编码
        base64_str = base64.b64encode(image_data).decode('utf-8')

        # 生成 data URI
        mime_type = self.MIME_TYPES[ext]
        data_uri = f'data:{mime_type};base64,{base64_str}'

        return data_uri

    def _compress_image(self, image_path: str) -> bytes:
        """
        压缩图片

        Args:
            image_path: 图片文件路径

        Returns:
            压缩后的图片二进制数据
        """
        # 打开图片
        img = Image.open(image_path)

        # 计算新尺寸（等比缩放）
        width, height = img.size
        if width > self.max_size or height > self.max_size:
            if width > height:
                new_width = self.max_size
                new_height = int(height * (self.max_size / width))
            else:
                new_height = self.max_size
                new_width = int(width * (self.max_size / height))

            img = img.resize((new_width, new_height), Image.LANCZOS)

        # 转换为 RGB（如果需要）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])  # 使用 alpha 通道作为 mask
                img = background
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # 保存到内存
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=self.quality, optimize=True)
        output.seek(0)

        return output.read()

    def get_image_info(self, image_path: str) -> dict:
        """
        获取图片信息

        Args:
            image_path: 图片文件路径

        Returns:
            图片信息字典，包括：原始尺寸、文件大小、格式等
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        img = Image.open(image_path)
        file_size = os.path.getsize(image_path)

        return {
            'path': image_path,
            'format': img.format,
            'mode': img.mode,
            'size': img.size,  # (width, height)
            'width': img.width,
            'height': img.height,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2)
        }


def encode_single_image(image_path: str, max_size: Optional[int] = None, quality: int = 85) -> str:
    """
    便捷函数：编码单张图片

    Args:
        image_path: 图片文件路径
        max_size: 图片最大尺寸
        quality: JPEG 压缩质量

    Returns:
        base64 data URI 字符串

    Example:
        >>> data_uri = encode_single_image('images/fig1.png')
        >>> print(data_uri[:100])  # 打印前100个字符
        data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
    """
    encoder = ImageBase64Encoder(max_size=max_size, quality=quality)
    return encoder.encode_image(image_path)


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("用法: python image_base64_encoder.py <图片路径> [最大尺寸] [质量]")
        print("示例: python image_base64_encoder.py images/fig1.png 1280 85")
        sys.exit(1)

    image_path = sys.argv[1]
    max_size = int(sys.argv[2]) if len(sys.argv) > 2 else None
    quality = int(sys.argv[3]) if len(sys.argv) > 3 else 85

    try:
        encoder = ImageBase64Encoder(max_size=max_size, quality=quality)

        # 显示图片信息
        print("=" * 70)
        print("图片信息")
        print("=" * 70)
        info = encoder.get_image_info(image_path)
        print(f"路径: {info['path']}")
        print(f"格式: {info['format']}")
        print(f"尺寸: {info['width']} x {info['height']}")
        print(f"文件大小: {info['file_size_mb']} MB")
        print()

        # 编码
        print("正在编码为 base64...")
        data_uri = encoder.encode_image(image_path)

        # 统计信息
        print("=" * 70)
        print("编码结果")
        print("=" * 70)
        print(f"Data URI 长度: {len(data_uri)} 字符")
        print(f"Data URI 前100字符: {data_uri[:100]}...")
        print()
        print("✅ 编码成功！")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
