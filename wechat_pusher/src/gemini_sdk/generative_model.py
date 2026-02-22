#!/usr/bin/env python3
"""主要模型类，借鉴官方SDK设计"""

import os
from collections.abc import AsyncGenerator
from typing import Any

from src.utils.logger import get_logger
from .chat import ChatSession
from .config import GeminiConfig, GenerationConfig
from .content import Content
from .data_models import Content as ContentModel
from .data_models import CountTokensResponse, GenerateContentResponse
from .exceptions import GeminiValidationError
from .http_client import HttpClient


class GenerativeModel:
    """主要模型类，借鉴官方SDK设计"""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        api_key: str | None = None,
        base_url: str = "http://192.168.100.220:8999",
        generation_config: GenerationConfig | None = None,
        timeout: float = 30.0,
    ):
        self.model_name = model_name
        self.config = GeminiConfig(api_key=api_key, base_url=base_url)
        self.generation_config = generation_config or GenerationConfig()
        self._http_client = HttpClient(self.config, timeout=timeout)

    async def generate_content(
        self,
        contents: str | dict[str, Any] | list[dict[str, Any]],
        generation_config: GenerationConfig | None = None,
        *,
        tools: list[dict[str, Any]] | None = None,
        safety_settings: list[dict[str, Any]] | None = None,
        system_instruction: str | dict[str, Any] | list[Any] | None = None,
        tool_config: dict[str, Any] | None = None,
        function_responses: list[dict[str, Any]] | None = None,
        tool_config_overrides: dict[str, Any] | None = None,
        stream_options: dict[str, Any] | None = None,
    ) -> GenerateContentResponse:
        """生成内容"""
        config = generation_config or self.generation_config
        request = self._build_request(
            contents,
            config,
            tools=tools,
            safety_settings=safety_settings,
            system_instruction=system_instruction,
            tool_config=tool_config,
            function_responses=function_responses,
            tool_config_overrides=tool_config_overrides,
            stream_options=stream_options,
        )
        response = await self._http_client.post(
            f"/v1beta/models/{self.model_name}:generateContent", request
        )

        # 记录API响应调试信息（仅在调试模式下）
        if (
            isinstance(response, dict)
            and "candidates" in response
            and os.getenv("DEBUG_GEMINI_SDK", "false").lower() == "true"
        ):
            logger = get_logger("gemini_sdk")

            candidate = response.get("candidates", [{}])[0]
            content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            logger.debug(f"Gemini API response for model {self.model_name}")
            logger.debug(f"Response text (first 300 chars): {content[:300]}...")
            logger.debug(f"Response length: {len(content)}")
            logger.debug(f"Has grounding: {'groundingMetadata' in candidate}")
            if "groundingMetadata" in candidate:
                metadata = candidate["groundingMetadata"]
                chunks_count = len(metadata.get("groundingChunks", []))
                logger.debug(f"Grounding chunks: {chunks_count}")

        return GenerateContentResponse.from_dict(response)

    async def generate_content_async(
        self,
        contents: str | dict[str, Any] | list[dict[str, Any]],
        generation_config: GenerationConfig | None = None,
        *,
        tools: list[dict[str, Any]] | None = None,
        safety_settings: list[dict[str, Any]] | None = None,
        system_instruction: str | dict[str, Any] | list[Any] | None = None,
        tool_config: dict[str, Any] | None = None,
        function_responses: list[dict[str, Any]] | None = None,
        tool_config_overrides: dict[str, Any] | None = None,
        stream_options: dict[str, Any] | None = None,
    ) -> AsyncGenerator[ContentModel, None]:
        """异步流式生成内容"""
        config = generation_config or self.generation_config
        request = self._build_request(
            contents,
            config,
            tools=tools,
            safety_settings=safety_settings,
            system_instruction=system_instruction,
            tool_config=tool_config,
            function_responses=function_responses,
            tool_config_overrides=tool_config_overrides,
            stream_options=stream_options,
        )

        async for chunk in self._http_client.stream(
            f"/v1beta/models/{self.model_name}:streamGenerateContent", request
        ):
            yield ContentModel.from_dict(chunk)

    async def count_tokens(
        self,
        contents: str | dict[str, Any] | list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        system_instruction: str | dict[str, Any] | list[Any] | None = None,
    ) -> CountTokensResponse:
        """Token计数"""
        request = self._build_request(
            contents,
            generation_config=None,
            tools=tools,
            system_instruction=system_instruction,
        )
        response = await self._http_client.post(
            f"/v1beta/models/{self.model_name}:countTokens", request
        )
        return CountTokensResponse.from_dict(response)

    def start_chat(
        self,
        context: str | None = None,
        history: list[dict[str, Any]] | None = None,
        generation_config: GenerationConfig | None = None,
    ) -> ChatSession:
        """开始聊天，返回ChatSession"""
        return ChatSession(
            model=self,
            context=context,
            history=history or [],
            generation_config=generation_config or self.generation_config,
        )

    def _build_request(
        self,
        contents: str | dict[str, Any] | list[dict[str, Any]],
        generation_config: GenerationConfig | None = None,
        *,
        tools: list[dict[str, Any]] | None = None,
        safety_settings: list[dict[str, Any]] | None = None,
        system_instruction: str | dict[str, Any] | list[Any] | None = None,
        tool_config: dict[str, Any] | None = None,
        function_responses: list[dict[str, Any]] | None = None,
        tool_config_overrides: dict[str, Any] | None = None,
        stream_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """构建请求"""
        # 标准化内容格式
        normalized_contents = Content.normalize(contents)

        # 构建请求体
        request: dict[str, Any] = {
            "contents": normalized_contents,
        }

        # 添加生成配置
        if generation_config:
            gen_config_dict = generation_config.to_dict()
            if gen_config_dict:
                request["generationConfig"] = gen_config_dict

        if tools:
            request["tools"] = tools
        if safety_settings:
            request["safetySettings"] = safety_settings
        if system_instruction:
            request["systemInstruction"] = self._normalize_system_instruction(system_instruction)
        if tool_config:
            request["toolConfig"] = tool_config
        if function_responses:
            request["functionResponses"] = function_responses
        if tool_config_overrides:
            request["toolConfigOverrides"] = tool_config_overrides
        if stream_options:
            request["streamOptions"] = stream_options

        return request

    def _normalize_system_instruction(
        self, instruction: str | dict[str, Any] | list[Any]
    ) -> dict[str, Any]:
        """标准化systemInstruction格式"""
        if isinstance(instruction, str):
            return {"role": "system", "parts": [{"text": instruction}]}

        if isinstance(instruction, dict):
            normalized = instruction.copy()
            normalized.setdefault("role", "system")
            if "parts" not in normalized or not isinstance(normalized["parts"], list):
                raise GeminiValidationError("system_instruction 必须包含 parts 列表")
            return normalized

        if isinstance(instruction, list):
            parts: list[dict[str, Any]] = []
            for item in instruction:
                if isinstance(item, str):
                    parts.append({"text": item})
                elif isinstance(item, dict):
                    if "text" in item:
                        parts.append(item)
                    else:
                        raise GeminiValidationError(
                            "system_instruction 列表中的字典必须包含 text 字段"
                        )
                else:
                    raise GeminiValidationError(
                        "system_instruction 列表元素必须是字符串或包含 text 的字典"
                    )

            if not parts:
                raise GeminiValidationError("system_instruction 至少需要一个有效的部分")

            return {"role": "system", "parts": parts}

        raise GeminiValidationError("system_instruction 类型不受支持")


# 为了向后兼容，提供别名
GeminiClient = GenerativeModel
