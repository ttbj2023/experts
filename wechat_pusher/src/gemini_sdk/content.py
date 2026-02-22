#!/usr/bin/env python3
"""多模态内容类型"""

import base64
import mimetypes
from pathlib import Path
from typing import Any


class GeminiContentError(Exception):
    """Gemini内容错误"""


def _get_mime_type(file_path: str) -> str:
    """获取文件的MIME类型"""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        # 根据文件扩展名猜测
        ext = Path(file_path).suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")
    return mime_type


class Content:
    """多模态内容类型，支持文本、图片、音频、视频"""

    @staticmethod
    def from_text(text: str) -> dict[str, Any]:
        """文本内容"""
        return {"role": "user", "parts": [{"text": text}]}

    @staticmethod
    def from_image(image_path: str, text: str | None = None) -> dict[str, Any]:
        """图片内容"""
        try:
            with Path(image_path).open("rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            mime_type = _get_mime_type(image_path)
            parts: list[dict[str, Any]] = [
                {"inline_data": {"mime_type": mime_type, "data": image_data}}
            ]

            if text:
                parts.append({"text": text})

        except FileNotFoundError as err:
            raise GeminiContentError("File not found") from err
        else:
            return {"role": "user", "parts": parts}

    @staticmethod
    def from_audio(audio_path: str, text: str | None = None) -> dict[str, Any]:
        """音频内容"""
        with Path(audio_path).open("rb") as f:
            audio_data = base64.b64encode(f.read()).decode()

        mime_type = _get_mime_type(audio_path)
        parts: list[dict[str, Any]] = [
            {"inline_data": {"mime_type": mime_type, "data": audio_data}}
        ]

        if text:
            parts.append({"text": text})

        return {"role": "user", "parts": parts}

    @staticmethod
    def from_video(video_path: str, text: str | None = None) -> dict[str, Any]:
        """视频内容"""
        with Path(video_path).open("rb") as f:
            video_data = base64.b64encode(f.read()).decode()

        mime_type = _get_mime_type(video_path)
        parts: list[dict[str, Any]] = [
            {"inline_data": {"mime_type": mime_type, "data": video_data}}
        ]

        if text:
            parts.append({"text": text})

        return {"role": "user", "parts": parts}

    @staticmethod
    def from_mixed(text: str, media_files: list[str]) -> dict[str, Any]:
        """混合内容（文本+多媒体）"""
        parts: list[dict[str, Any]] = [{"text": text}]

        for file_path in media_files:
            try:
                with Path(file_path).open("rb") as f:
                    file_data = base64.b64encode(f.read()).decode()

                mime_type = _get_mime_type(file_path)
                parts.append({"inline_data": {"mime_type": mime_type, "data": file_data}})
            except FileNotFoundError:
                # 如果文件不存在，跳过该文件
                continue

        return {"role": "user", "parts": parts}

    @staticmethod
    def normalize(content: str | dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
        """标准化内容格式"""
        if isinstance(content, str):
            return [Content.from_text(content)]
        elif isinstance(content, dict):
            return [content]
        elif isinstance(content, list):
            return content
        else:
            raise GeminiContentError("Invalid content type")
