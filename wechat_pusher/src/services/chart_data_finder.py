#!/usr/bin/env python3
"""
图表数据查找服务

使用Gemini 2.5 Flash + Google Search自动查找图表所需的真实数据
"""

import asyncio
import json
import os
import re
from typing import Dict, Optional, List
from pathlib import Path

from src.gemini_sdk import (
    GenerativeModel,
    GenerationConfig,
    create_google_search_tool,
    GenerateContentResponse
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChartDataFinder:
    """图表数据查找器 - 使用Gemini + Google Search查找真实数据"""

    def __init__(self):
        """初始化数据查找器"""
        self.api_key = os.getenv("GEMINI_API_KEY", "test1234")
        self.base_url = os.getenv("GEMINI_BASE_URL", "http://192.168.100.220:8999")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # 初始化Gemini模型
        self.model = GenerativeModel(
            model_name=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url
        )

        self.available = True
        logger.info(f"✅ ChartDataFinder初始化成功 (endpoint: {self.base_url})")

    def is_available(self) -> bool:
        """检查查找器是否可用"""
        return self.available

    async def find_chart_data_async(
        self,
        description: str,
        chart_type_hint: str = None
    ) -> Optional[Dict]:
        """
        异步查找图表数据

        Args:
            description: 图表描述，例如 "柱状图，显示运营商税率从6%调整到9%"
            chart_type_hint: 图表类型提示 ("line", "bar", "pie")

        Returns:
            dict: 查找结果，格式：
                {
                    "found": true,
                    "chart_type": "line|bar|pie",
                    "labels": ["2020", "2021", ...],
                    "values": [100, 150, ...],
                    "xlabel": "年份",
                    "ylabel": "数值",
                    "source": "数据来源描述",
                    "grounding": [
                        {"uri": "https://...", "title": "..."}
                    ]
                }
                如果失败返回 {"found": false, "reason": "..."}
        """
        if not self.available:
            return {"found": False, "reason": "ChartDataFinder不可用"}

        try:
            logger.info(f"🔍 使用Gemini查找图表数据...")
            logger.debug(f"  描述: {description}")

            # 构建查询提示词
            prompt = self._build_search_prompt(description, chart_type_hint)

            # 调用Gemini（带Google Search工具）
            generation_config = GenerationConfig(
                temperature=0.2,  # 低温度以获得更准确的数据
                max_output_tokens=2048
            )

            response: GenerateContentResponse = await self.model.generate_content(
                contents=prompt,
                generation_config=generation_config,
                tools=[create_google_search_tool()]
            )

            # 解析响应
            result = self._parse_gemini_response(response, description)

            if result and result.get("found"):
                logger.info(f"✅ 成功找到图表数据")
                logger.info(f"  图表类型: {result.get('chart_type')}")
                logger.info(f"  数据点数: {len(result.get('labels', []))}")
                logger.info(f"  来源: {result.get('source', 'N/A')}")
            else:
                logger.warning(f"⚠️  未找到合适的图表数据")

            return result

        except Exception as e:
            logger.error(f"❌ Gemini查找失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {"found": False, "reason": str(e)}

    def find_chart_data(
        self,
        description: str,
        chart_type_hint: str = None
    ) -> Optional[Dict]:
        """
        同步版本的图表数据查找

        Args:
            同上

        Returns:
            同上
        """
        if not self.available:
            return {"found": False, "reason": "ChartDataFinder不可用"}

        try:
            # 在新的事件循环中运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.find_chart_data_async(description, chart_type_hint)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"❌ 同步调用Gemini失败: {e}")
            return {"found": False, "reason": str(e)}

    def _build_search_prompt(self, description: str, chart_type_hint: str = None) -> str:
        """
        构建搜索提示词

        Args:
            description: 图表描述
            chart_type_hint: 图表类型提示

        Returns:
            str: 完整的查询提示词
        """
        # 推断图表类型
        if not chart_type_hint:
            if "折线图" in description or "趋势" in description:
                chart_type_hint = "line"
            elif "柱状图" in description or "对比" in description:
                chart_type_hint = "bar"
            elif "饼图" in description or "占比" in description or "份额" in description:
                chart_type_hint = "pie"

        chart_type_map = {
            "line": "折线图（趋势图）",
            "bar": "柱状图（对比图）",
            "pie": "饼图（占比图）"
        }

        chart_type_name = chart_type_map.get(chart_type_hint, "图表")

        prompt = f"""我需要为一个文章生成{chart_type_name}，请帮我查找准确的数据。

**图表描述**：{description}

**要求**：
1. 使用Google搜索查找真实、准确的数据
2. 数据必须是最近发布的（优先2024-2025年的数据）
3. 数据来源必须是权威机构、官方发布或知名媒体
4. 返回JSON格式，严格按照以下格式：

```json
{{
  "found": true,
  "chart_type": "{chart_type_hint or 'line'}",
  "title": "图表标题",
  "labels": ["标签1", "标签2", "标签3"],
  "values": [数值1, 数值2, 数值3],
  "xlabel": "横轴标签",
  "ylabel": "纵轴标签（包含单位）",
  "source": "数据来源（机构名 + 发布时间）",
  "notes": "数据说明（如果有特殊含义或限制）"
}}
```

**注意事项**：
- 如果找不到确切数据，设置 found: false 并在 notes 中说明原因
- 数值必须是具体的数字，不要使用估算或模糊表述
- labels 和 values 的数量必须一致
- 如果是百分比数据，请在数值中包含%，例如 25.5（表示25.5%）
- source 必须包含具体的数据来源

请开始搜索并返回结果。"""

        return prompt

    def _parse_gemini_response(
        self,
        response: GenerateContentResponse,
        original_description: str
    ) -> Optional[Dict]:
        """
        解析Gemini响应

        Args:
            response: Gemini响应对象
            original_description: 原始图表描述

        Returns:
            dict: 解析后的数据
        """
        # 提取grounding信息
        grounding_chunks = response.grounding_chunks or []
        search_entry = response.search_entry_point or {}

        # 提取文本内容
        text = response.text or ""
        logger.debug(f"  Gemini响应: {text[:200]}...")

        # 方法1：查找JSON代码块
        json_pattern = r'```(?:json)?\s*\n?(\{.*?\})\s?\n?```'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(1))
                if self._validate_chart_data(data):
                    # 添加grounding信息
                    data["grounding"] = grounding_chunks
                    data["search_entry"] = search_entry
                    data["found"] = True
                    return data
                else:
                    logger.warning("JSON数据验证失败")
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析失败: {e}")

        # 方法2：查找裸JSON对象
        json_pattern2 = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern2, text, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if self._validate_chart_data(data):
                    data["grounding"] = grounding_chunks
                    data["search_entry"] = search_entry
                    data["found"] = True
                    return data
            except json.JSONDecodeError:
                continue

        # 未找到有效数据
        return {
            "found": False,
            "reason": "无法从Gemini响应中提取有效数据",
            "grounding": grounding_chunks
        }

    def _validate_chart_data(self, data: Dict) -> bool:
        """
        验证图表数据的完整性

        Args:
            data: 待验证的数据字典

        Returns:
            bool: 是否有效
        """
        required_fields = ["labels", "values"]

        # 检查必需字段
        for field in required_fields:
            if field not in data:
                return False

        # 检查labels和values长度是否一致
        labels = data.get("labels", [])
        values = data.get("values", [])

        if not isinstance(labels, list) or not isinstance(values, list):
            return False

        if len(labels) != len(values):
            return False

        # 至少需要2个数据点
        if len(labels) < 2:
            return False

        # 检查values是否为数字
        try:
            [float(v) for v in values]
        except (ValueError, TypeError):
            return False

        return True


# 全局单例
_chart_data_finder = None


def get_chart_data_finder() -> ChartDataFinder:
    """获取ChartDataFinder单例"""
    global _chart_data_finder
    if _chart_data_finder is None:
        _chart_data_finder = ChartDataFinder()
    return _chart_data_finder
