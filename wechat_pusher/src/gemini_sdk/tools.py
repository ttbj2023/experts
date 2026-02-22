#!/usr/bin/env python3
"""Gemini 原生工具配置工厂

为常用官方工具提供轻量级的字典工厂，避免引入复杂的类体系。
"""

from __future__ import annotations

from typing import Any


def create_google_search_tool() -> dict[str, Any]:
    """创建 Google Search 工具配置"""
    return {"google_search": {}}


def create_url_retrieval_tool() -> dict[str, Any]:
    """创建 URL Context 工具配置"""
    return {"url_context": {}}


def create_code_execution_tool() -> dict[str, Any]:
    """创建代码执行工具配置"""
    return {"code_execution": {}}


def create_function_tool(
    *,
    name: str,
    description: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """创建函数调用工具配置"""
    return {
        "function_declarations": [
            {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        ]
    }


def create_function_response(
    *,
    name: str,
    response: Any,
) -> dict[str, Any]:
    """将函数执行结果包装成Gemini可识别的响应结构"""
    return {"name": name, "response": response}
