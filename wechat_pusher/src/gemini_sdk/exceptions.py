#!/usr/bin/env python3
"""异常类定义"""


class GeminiError(Exception):
    """Gemini SDK 基础异常"""


class GeminiAuthenticationError(GeminiError):
    """认证错误"""


class GeminiConnectionError(GeminiError):
    """连接错误"""


class GeminiTimeoutError(GeminiError):
    """超时错误"""


class GeminiRateLimitError(GeminiError):
    """速率限制错误"""


class GeminiValidationError(GeminiError):
    """验证错误"""
