#!/usr/bin/env python3
"""配置管理"""

import os
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


class GeminiConfigurationError(Exception):
    """Gemini配置错误"""


@dataclass
class GenerationConfig:
    """生成配置类，管理所有生成参数"""

    temperature: float | None = 0.7
    top_p: float | None = 0.9
    top_k: int | None = 40
    max_output_tokens: int | None = 8192
    candidate_count: int | None = 1
    stop_sequences: list[str] = field(default_factory=list)
    response_mime_type: str | None = None
    response_schema: Any | None = None
    seed: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    thinking_budget: int | None = None  # 思考预算参数
    extra_options: dict[str, Any] = field(default_factory=dict)

    def _serialize_schema(self) -> dict[str, Any] | None:
        """将响应结构转换为API可接受的字典格式"""
        schema = self.response_schema
        if schema is None:
            return None

        if isinstance(schema, dict):
            return schema

        if isinstance(schema, type) and issubclass(schema, BaseModel):
            # Pydantic v2推荐使用model_json_schema
            return schema.model_json_schema()

        if isinstance(schema, BaseModel):
            return schema.model_json_schema()

        # 兼容TypedDict等对象
        to_schema = getattr(schema, "model_json_schema", None) or getattr(schema, "schema", None)
        if callable(to_schema):
            result = to_schema()
            if isinstance(result, dict):
                return result

        raise TypeError("response_schema 必须是 dict 或支持 model_json_schema/schema 方法的对象")

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        config: dict[str, Any] = {}

        self._add_basic_config(config)
        self._add_response_config(config)
        self._add_penalty_config(config)
        self._add_thinking_config(config)
        self._add_extra_config(config)

        return config

    def _add_basic_config(self, config: dict[str, Any]) -> None:
        """添加基本配置参数"""
        if self.temperature is not None:
            config["temperature"] = self.temperature
        if self.top_p is not None:
            config["topP"] = self.top_p
        if self.top_k is not None:
            config["topK"] = self.top_k
        if self.max_output_tokens is not None:
            config["maxOutputTokens"] = self.max_output_tokens
        if self.candidate_count is not None:
            config["candidateCount"] = self.candidate_count
        if self.stop_sequences:
            config["stopSequences"] = self.stop_sequences

    def _add_response_config(self, config: dict[str, Any]) -> None:
        """添加响应相关配置"""
        if self.response_mime_type:
            config["responseMimeType"] = self.response_mime_type
        schema = self._serialize_schema()
        if schema:
            config["responseSchema"] = schema
        if self.seed is not None:
            config["seed"] = self.seed

    def _add_penalty_config(self, config: dict[str, Any]) -> None:
        """添加惩罚相关配置"""
        if self.presence_penalty is not None:
            config["presencePenalty"] = self.presence_penalty
        if self.frequency_penalty is not None:
            config["frequencyPenalty"] = self.frequency_penalty

    def _add_thinking_config(self, config: dict[str, Any]) -> None:
        """添加思考配置参数"""
        if self.thinking_budget is not None:
            # 根据官方文档，thinking_config应该嵌套在config中
            config["thinkingConfig"] = {"thinkingBudget": self.thinking_budget}

    def _add_extra_config(self, config: dict[str, Any]) -> None:
        """添加额外配置"""
        if self.extra_options:
            config.update(self.extra_options)


class GeminiConfig:
    """Gemini配置类"""

    def __init__(self, api_key: str | None = None, base_url: str = "http://192.168.100.220:8999"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = base_url

        # 如果没有API密钥，使用默认值
        if not self.api_key:
            self.api_key = "test1234"

    @property
    def headers(self) -> dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["x-goog-api-key"] = self.api_key
        return headers
