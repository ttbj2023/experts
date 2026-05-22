"""睡眠有效性分析器

仅判断睡眠记录是否有效（asleep_minutes > 60 分钟），
不提供评分或分类。
"""

import logging
from typing import Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)


class SleepQualityAnalyzer:
    """睡眠有效性分析器 - 简化版

    判定逻辑：
    - asleep_minutes > 60 → is_valid_sleep_day = True
    - 否则 → is_valid_sleep_day = False
    """

    MIN_VALID_ASLEEP_MINUTES = 60

    def __init__(self, config=None):
        self.config = config or {}

    def batch_analyze(self, sleep_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """批量标记睡眠有效性

        Args:
            sleep_df: 睡眠数据 DataFrame

        Returns:
            添加了 is_valid_sleep_day 字段的 DataFrame
        """
        result_df = sleep_df.copy()

        result_df['is_valid_sleep_day'] = (
            result_df['asleep_minutes'].fillna(0) > self.MIN_VALID_ASLEEP_MINUTES
        )

        valid_count = result_df['is_valid_sleep_day'].sum()
        total_count = len(result_df)
        logger.info(
            f"睡眠有效性标记完成: {valid_count}/{total_count} 天有效 "
            f"({valid_count / total_count * 100:.1f}%)" if total_count > 0 else "睡眠有效性标记完成: 无数据"
        )

        return result_df
