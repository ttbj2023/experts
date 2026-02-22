#!/usr/bin/env python3
"""数据模型定义"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


def _extract_text(parts: list[dict[str, Any]]) -> str:
    """拼接文本内容"""
    return "".join(
        part["text"] for part in parts if "text" in part and isinstance(part["text"], str)
    )


def _try_parse_json(text: str) -> Any:
    """尝试解析JSON文本"""
    cleaned = text.strip()
    if not cleaned or cleaned[0] not in "[{":
        return None

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def _normalize_function_args(args: Any) -> dict[str, Any]:
    """确保函数调用参数为字典"""
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            parsed = json.loads(args)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {"__raw__": args}
    return {"__raw__": args}


@dataclass
class ToolCall:
    """工具调用信息"""

    name: str
    args: dict[str, Any]
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerateContentResponse:
    """生成内容响应模型"""

    text: str
    usage_metadata: dict[str, Any]
    finish_reason: str
    response_id: str
    candidates: list[dict[str, Any]] = field(default_factory=list)
    grounding_metadata: dict[str, Any] | None = None
    grounding_chunks: list[dict[str, Any]] = field(default_factory=list)
    search_entry_point: dict[str, Any] | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    parsed: Any | None = None
    safety_ratings: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GenerateContentResponse:
        """从字典创建响应对象"""
        candidates = data.get("candidates", []) or []
        usage_metadata = data.get("usageMetadata", {})
        response_id = data.get("responseId", "")
        response_metadata = data.get("responseMetadata", {})

        text = ""
        parsed = None
        grounding_metadata = None
        grounding_chunks: list[dict[str, Any]] = []
        search_entry_point = None
        safety_ratings: list[dict[str, Any]] = []
        tool_calls: list[ToolCall] = []

        for index, candidate in enumerate(candidates):
            content = candidate.get("content", {}) if isinstance(candidate, dict) else {}
            parts = content.get("parts", []) if isinstance(content, dict) else []

            if index == 0:
                text = _extract_text(parts)
                grounding_metadata = candidate.get("groundingMetadata")
                if grounding_metadata:
                    grounding_chunks = grounding_metadata.get("groundingChunks", []) or []
                    search_entry_point = grounding_metadata.get("searchEntryPoint") or data.get(
                        "searchEntryPoint"
                    )

                if not search_entry_point:
                    search_entry_point = data.get("searchEntryPoint")

                parsed = _try_parse_json(text)

            tool_calls.extend(cls._parse_tool_calls(candidate))
            safety_ratings.extend(candidate.get("safetyRatings", []) or [])

        finish_reason = candidates[0].get("finishReason", "UNKNOWN") if candidates else "UNKNOWN"

        response_mime_type = response_metadata.get("responseMimeType")
        if parsed is None and response_mime_type == "application/json":
            parsed = _try_parse_json(text)

        if tool_calls:
            unique_calls: list[ToolCall] = []
            seen: set[tuple[str, str]] = set()
            for call in tool_calls:
                signature = (call.name, repr(call.args))
                if signature in seen:
                    continue
                unique_calls.append(call)
                seen.add(signature)
            tool_calls = unique_calls

        metadata = {
            "promptFeedback": data.get("promptFeedback"),
            "responseMetadata": response_metadata,
        }

        return cls(
            text=text,
            usage_metadata=usage_metadata,
            finish_reason=finish_reason,
            response_id=response_id,
            candidates=candidates,
            grounding_metadata=grounding_metadata,
            grounding_chunks=grounding_chunks,
            search_entry_point=search_entry_point,
            tool_calls=tool_calls,
            parsed=parsed,
            safety_ratings=safety_ratings,
            metadata=metadata,
        )

    @staticmethod
    def _parse_tool_calls(candidate: dict[str, Any]) -> list[ToolCall]:
        """解析工具调用结构"""
        calls: list[ToolCall] = []

        # 从toolCalls字段中解析
        for call in candidate.get("toolCalls", []) or []:
            function_call = call.get("functionCall", {})
            if not function_call:
                continue
            name = function_call.get("name", "")
            args = _normalize_function_args(function_call.get("args", {}))
            calls.append(ToolCall(name=name, args=args, raw=function_call))

        # 从parts中的functionCall解析（流式响应）
        content = candidate.get("content", {})
        parts = content.get("parts", []) if isinstance(content, dict) else []
        for part in parts:
            function_call = part.get("functionCall") if isinstance(part, dict) else None
            if not function_call:
                continue
            name = function_call.get("name", "")
            args = _normalize_function_args(function_call.get("args", {}))
            calls.append(ToolCall(name=name, args=args, raw=function_call))

        return calls


@dataclass
class CountTokensResponse:
    """Token计数响应模型"""

    total_tokens: int
    prompt_tokens: int
    candidates_tokens: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CountTokensResponse:
        """从字典创建响应对象"""
        return cls(
            total_tokens=data.get("totalTokens", 0),
            prompt_tokens=data.get("promptTokens", 0),
            candidates_tokens=data.get("candidatesTokens", 0),
        )


@dataclass
class Content:
    """内容块模型"""

    text: str
    role: str = "model"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Content:
        """从字典创建内容对象"""
        text = ""
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            text = "".join(part.get("text", "") for part in parts)

        return cls(text=text, role="model")
