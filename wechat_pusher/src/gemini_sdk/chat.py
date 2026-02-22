#!/usr/bin/env python3
"""聊天会话类，完全借鉴官方SDK设计"""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

from .data_models import Content as ContentModel
from .data_models import GenerateContentResponse


class GeminiChatError(Exception):
    """Gemini聊天错误"""


if TYPE_CHECKING:
    from .config import GenerationConfig
    from .generative_model import GenerativeModel


class ChatSession:
    """聊天会话类，完全借鉴官方SDK设计"""

    def __init__(
        self,
        model: "GenerativeModel",
        context: str | None = None,
        history: list[dict[str, Any]] | None = None,
        generation_config: "GenerationConfig | None" = None,
    ):
        self.model = model
        self.context = context
        self.history: list[dict[str, Any]] = history or []
        self.generation_config = generation_config or model.generation_config
        self._last_response: GenerateContentResponse | None = None

    async def send_message(
        self, message: str | dict[str, Any] | list[dict[str, Any]]
    ) -> GenerateContentResponse:
        """发送消息"""
        contents = self._build_contents_with_history(message)
        response = await self.model.generate_content(contents, self.generation_config)
        self._update_history(message, response)
        self._last_response = response
        return response

    async def send_message_async(
        self, message: str | dict[str, Any] | list[dict[str, Any]]
    ) -> AsyncGenerator[ContentModel, None]:
        """异步发送消息"""
        contents = self._build_contents_with_history(message)
        async for content in self.model.generate_content_async(contents, self.generation_config):
            yield content

    def get_history(self) -> list[dict[str, Any]]:
        """获取完整历史"""
        return self.history.copy()

    def rewrite_history(self, history: list[dict[str, Any]]) -> None:
        """重写历史"""
        self.history = history.copy()

    @property
    def last(self) -> GenerateContentResponse | None:
        """获取最后一条响应"""
        return self._last_response

    def _build_contents_with_history(
        self, message: str | dict[str, Any] | list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """构建包含历史的完整内容"""
        contents = []

        # 添加上下文
        if self.context:
            contents.append({"role": "user", "parts": [{"text": f"Context: {self.context}"}]})

        # 添加历史
        contents.extend(self.history)

        # 添加当前消息
        if isinstance(message, str):
            contents.append({"role": "user", "parts": [{"text": message}]})
        elif isinstance(message, dict):
            contents.append(message)
        elif isinstance(message, list):
            contents.extend(message)
        else:
            raise GeminiChatError("Invalid message type")

        return contents

    def _update_history(
        self,
        message: str | dict[str, Any] | list[dict[str, Any]],
        response: GenerateContentResponse,
    ) -> None:
        """更新对话历史"""
        # 添加用户消息
        if isinstance(message, str):
            self.history.append({"role": "user", "parts": [{"text": message}]})
        elif isinstance(message, dict):
            self.history.append(message)
        elif isinstance(message, list):
            self.history.extend(message)

        # 添加模型响应
        if response.text:
            self.history.append({"role": "model", "parts": [{"text": response.text}]})
