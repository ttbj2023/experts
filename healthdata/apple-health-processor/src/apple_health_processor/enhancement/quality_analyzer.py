"""数据质量分析器

通过简化的规则判定设备佩戴状态和低活动日。
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class QualityAnalyzer:
    """质量分析器 - 简化版

    判定逻辑：
    1. 佩戴状态：stand_hours > 0 或 active_energy > 0 → "worn"，否则 → "not_worn"
    2. 低活动日：steps < 1000 且佩戴 → True
    """

    LOW_ACTIVITY_STEPS_THRESHOLD = 1000

    def __init__(self, config: Optional[Dict] = None):
        self.config = config if config is not None else {}

    def analyze_daily_quality(self, daily_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析单日数据质量

        Args:
            daily_data: 单日数据字典

        Returns:
            质量分析结果字典
        """
        stand_hours = daily_data.get("stand_hours", 0) or 0
        active_energy = daily_data.get("active_energy_kcal", 0) or 0
        steps = daily_data.get("steps", 0) or 0

        wear_status = "worn" if (stand_hours > 0 or active_energy > 0) else "not_worn"

        is_low_activity = (
            steps < self.LOW_ACTIVITY_STEPS_THRESHOLD
            and wear_status == "worn"
        )

        return {
            "wear_status": wear_status,
            "is_low_activity_day": is_low_activity,
        }

    def batch_analyze(self, daily_data_list: List[Dict]) -> List[Dict]:
        """批量分析多日数据质量"""
        return [self.analyze_daily_quality(d) for d in daily_data_list]

    def get_quality_summary(self, quality_data: List[Dict]) -> Dict[str, Any]:
        """获取质量摘要统计"""
        if not quality_data:
            return {
                "total_days": 0,
                "worn_days": 0,
                "not_worn_days": 0,
                "low_activity_days": 0,
            }

        total = len(quality_data)
        worn = sum(1 for d in quality_data if d.get("wear_status") == "worn")
        not_worn = sum(1 for d in quality_data if d.get("wear_status") == "not_worn")
        low_activity = sum(1 for d in quality_data if d.get("is_low_activity_day"))

        return {
            "total_days": total,
            "worn_days": worn,
            "not_worn_days": not_worn,
            "low_activity_days": low_activity,
        }
