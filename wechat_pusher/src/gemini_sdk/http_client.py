#!/usr/bin/env python3
"""HTTP客户端"""

import asyncio
import json
import logging
import secrets
import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from .config import GeminiConfig
from .exceptions import GeminiError

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP客户端，专门封装GARP Core API"""

    def __init__(self, config: GeminiConfig, timeout: float = 180.0):
        self.config = config
        self.timeout = timeout
        self.last_request_time: float = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        self.max_retries = 3
        self.base_retry_delay = 2.0  # Base delay for exponential backoff

    async def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """POST请求 with retry mechanism and rate limiting"""
        url = f"{self.config.base_url}{endpoint}"

        # Rate limiting
        await self._enforce_rate_limit()

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=data, headers=self.config.headers)

                    # Handle retryable status codes (429, 503)
                    if response.status_code in [429, 503]:
                        error_type = (
                            "Rate limited" if response.status_code == 429 else "Service unavailable"
                        )
                        retry_after = self._calculate_retry_delay(attempt)
                        logger.warning(
                            f"{error_type} ({response.status_code}). "
                            f"Retrying in {retry_after:.1f}s "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    data = response.json()

                    # Update last request time on success
                    self.last_request_time = time.time()
                    return data

            except httpx.HTTPStatusError as e:
                if e.response.status_code in [429, 503]:
                    # Will be handled by retry logic above
                    continue
                logger.exception(f"HTTP error {e.response.status_code}: {e}")
                raise
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt < self.max_retries - 1:
                    retry_delay = self._calculate_retry_delay(attempt)
                    logger.warning(
                        f"Request error: {e}. "
                        f"Retrying in {retry_delay:.1f}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                logger.exception(f"Request failed after {self.max_retries} attempts: {e}")
                raise

        # If we get here, all retries failed
        raise GeminiError(f"Failed to complete request after {self.max_retries} attempts")

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = self.base_retry_delay * (2**attempt)
        # Add jitter to avoid thundering herd
        jitter = 0.8 + (secrets.randbelow(401) / 1000)  # 0.8-1.2
        result = delay * jitter
        return float(result)

    async def _enforce_rate_limit(self) -> None:
        """Enforce minimum time between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def stream(
        self, endpoint: str, data: dict[str, Any]
    ) -> AsyncGenerator[dict[str, Any], None]:
        """流式请求"""
        url = f"{self.config.base_url}{endpoint}"

        async with (
            httpx.AsyncClient(timeout=self.timeout) as client,
            client.stream("POST", url, json=data, headers=self.config.headers) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data_str = line[6:].strip()
                        if data_str:
                            yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
