"""
图表数据研究辅助模块
直接调用tool_engine_local的ResearchAssistantTool
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Optional
import json
import re

# 添加tool_engine_local路径
TOOL_ENGINE_PATH = Path("/home/jsjrjft/project/tool_engine_local")
if TOOL_ENGINE_PATH.exists():
    sys.path.insert(0, str(TOOL_ENGINE_PATH))

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ResearchHelper:
    """图表数据研究助手"""

    def __init__(self):
        """初始化研究助手"""
        self.tool_engine_path = TOOL_ENGINE_PATH
        self.available = False

        # 检查是否可用
        try:
            # 尝试导入
            from src.tools.research_assistant import ResearchAssistantTool
            self.ResearchAssistantTool = ResearchAssistantTool
            self.available = True
            logger.info("✅ ResearchHelper初始化成功，tool_engine_local可用")
        except ImportError as e:
            logger.warning(f"⚠️  无法导入ResearchAssistantTool: {e}")
            logger.info("   图表数据研究功能将使用默认配置")
        except Exception as e:
            logger.warning(f"⚠️  ResearchHelper初始化失败: {e}")

    def is_available(self) -> bool:
        """检查研究助手是否可用"""
        return self.available

    async def research_chart_data(
        self,
        description: str,
        keywords: list[str],
        requirements: str
    ) -> Optional[Dict]:
        """
        研究图表数据

        Args:
            description: 图表描述
            keywords: 关键词列表
            requirements: 详细需求

        Returns:
            dict: 研究结果，格式：
                {
                    "found": true,
                    "chart_data": {
                        "type": "line|bar|pie",
                        "title": "图表标题",
                        "labels": [...],
                        "values": [...],
                        "xlabel": "...",
                        "ylabel": "..."
                    },
                    "source": "数据来源",
                    "notes": "说明"
                }
                如果失败返回 {"found": false, "reason": "..."}
        """
        if not self.available:
            return None

        try:
            logger.info("🔍 调用research_assistant查找图表数据...")

            # 切换到tool_engine目录
            original_cwd = os.getcwd()
            os.chdir(self.tool_engine_path)

            # 创建工具实例
            research_tool = self.ResearchAssistantTool()

            # 调用研究工具
            result = await research_tool.search(
                keywords=keywords,
                requirements=requirements,
                detail_level="comprehensive",
                speed_priority="thorough"
            )

            # 恢复工作目录
            os.chdir(original_cwd)

            # 解析结果
            parsed_data = self._parse_result(result)

            if parsed_data and parsed_data.get("found"):
                logger.info(f"✅ 成功找到图表数据，来源: {parsed_data.get('source', 'N/A')}")
            else:
                logger.warning("⚠️  research_assistant未找到合适的图表数据")

            return parsed_data

        except Exception as e:
            logger.error(f"❌ research_assistant调用失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {"found": False, "reason": str(e)}

    def research_chart_data_sync(
        self,
        description: str,
        keywords: list[str],
        requirements: str
    ) -> Optional[Dict]:
        """
        同步版本的图表数据研究

        Args:
            同上

        Returns:
            同上
        """
        if not self.available:
            return None

        try:
            # 在新的事件循环中运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.research_chart_data(description, keywords, requirements)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"❌ 同步调用research_assistant失败: {e}")
            return {"found": False, "reason": str(e)}

    def _parse_result(self, result: str) -> Optional[Dict]:
        """
        解析research_assistant的返回结果

        Args:
            result: 返回的文本

        Returns:
            dict: 解析后的数据
        """
        # 方法1：查找JSON代码块
        json_pattern = r'```(?:json)?\s*\n?(\{.*?\})\s?\n?```'
        match = re.search(json_pattern, result, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(1))
                # 确保包含found字段
                if "found" not in data:
                    # 检查是否有chart_data或data字段
                    if "chart_data" in data or "data" in data:
                        data["found"] = True
                        # 如果是旧格式(data字段)，转换为chart_data
                        if "data" in data and "chart_data" not in data:
                            data["chart_data"] = self._convert_to_chart_data(data["data"])
                    else:
                        data["found"] = False
                return data
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析失败: {e}")

        # 方法2：查找裸JSON对象
        json_pattern2 = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern2, result, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if "chart_data" in data or "data" in data:
                    if "found" not in data:
                        data["found"] = True
                        if "data" in data and "chart_data" not in data:
                            data["chart_data"] = self._convert_to_chart_data(data["data"])
                    return data
            except json.JSONDecodeError:
                continue

        logger.warning("无法从research_assistant结果中提取JSON数据")
        return {"found": False, "reason": "无法解析返回结果"}

    def _convert_to_chart_data(self, data: Dict) -> Dict:
        """
        将旧格式(data字段)转换为chart_data格式

        Args:
            data: 旧格式数据

        Returns:
            dict: chart_data格式
        """
        # 尝试推断图表类型
        labels = data.get("labels", [])
        values = data.get("values", [])
        xlabel = data.get("xlabel", "")
        ylabel = data.get("ylabel", "")

        # 如果没有指定类型，根据标签推断
        chart_type = "line"  # 默认
        if xlabel and "年" in xlabel:
            chart_type = "line"
        elif len(labels) <= 5 and not xlabel:
            chart_type = "pie"

        return {
            "type": chart_type,
            "title": data.get("title", "数据图表"),
            "labels": labels,
            "values": values,
            "xlabel": xlabel,
            "ylabel": ylabel
        }


# 全局单例
_research_helper = None


def get_research_helper() -> ResearchHelper:
    """获取ResearchHelper单例"""
    global _research_helper
    if _research_helper is None:
        _research_helper = ResearchHelper()
    return _research_helper
