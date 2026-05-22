"""滚动指标计算器

计算7日滚动均值指标，配合简化后的佩戴状态判定。
"""

import logging
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RollingCalculator:
    """滚动指标计算器 - 计算7日滚动均值

    支持以下指标：
    1. 体重7日均值 (weight_7day_avg)
    2. 步数7日均值 (steps_7day_avg)
    3. 每周运动分钟数 (exercise_weekly_total)
    4. 静息心率7日均值 (resting_hr_7day_avg)
    5. HRV 7日均值 (hrv_7day_avg)
    6. 低活动日数量 (low_activity_days_7day)
    """

    DEFAULT_WINDOW_DAYS = 7
    DEFAULT_MIN_VALID_DAYS = 4

    def __init__(self, config: Optional[Dict] = None):
        self.config = config if config is not None else {}
        self._load_rules()

    def _load_rules(self) -> None:
        rolling_config = self.config.get("rolling_metrics", {})

        self.window_days = rolling_config.get("window_days", self.DEFAULT_WINDOW_DAYS)
        self.min_valid_days = rolling_config.get("min_valid_days", self.DEFAULT_MIN_VALID_DAYS)

        anomaly_rules = rolling_config.get("anomaly_detection", {})

        weight_rules = anomaly_rules.get("weight", {})
        self.weight_max_daily_change = weight_rules.get("max_daily_change", 5.0)
        self.weight_min_value = weight_rules.get("min_value", 30)
        self.weight_max_value = weight_rules.get("max_value", 300)

        steps_rules = anomaly_rules.get("steps", {})
        self.steps_min_value = steps_rules.get("min_value", 0)
        self.steps_max_value = steps_rules.get("max_value", 100000)

        hr_rules = anomaly_rules.get("resting_hr", {})
        self.hr_min_value = hr_rules.get("min_value", 40)
        self.hr_max_value = hr_rules.get("max_value", 120)

        hrv_rules = anomaly_rules.get("hrv", {})
        self.hrv_min_value = hrv_rules.get("min_value", 10)
        self.hrv_max_value = hrv_rules.get("max_value", 200)

        exercise_rules = anomaly_rules.get("exercise", {})
        self.exercise_min_value = exercise_rules.get("min_value", 0)
        self.exercise_max_value = exercise_rules.get("max_value", 300)

        logger.debug(f"滚动计算规则已加载，窗口大小: {self.window_days}天")

    def calculate_all_rolling_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有滚动指标"""
        enhanced_df = df.copy()

        enhanced_df["weight_7day_avg"] = self.calculate_weight_7day_avg(df)
        enhanced_df["steps_7day_avg"] = self.calculate_steps_7day_avg(df)
        enhanced_df["exercise_weekly_total"] = self.calculate_exercise_weekly_total(df)
        enhanced_df["resting_hr_7day_avg"] = self.calculate_resting_hr_7day_avg(df)
        enhanced_df["hrv_7day_avg"] = self.calculate_hrv_7day_avg(df)
        enhanced_df["low_activity_days_7day"] = self.calculate_low_activity_days_7day(df)

        logger.info("所有滚动指标计算完成，新增6个指标字段")

        return enhanced_df

    def _exclude_not_worn(self, series: pd.Series, df: pd.DataFrame) -> pd.Series:
        """排除未佩戴天的数据"""
        result = series.copy()
        if "wear_status" in df.columns:
            result.loc[df["wear_status"] == "not_worn"] = np.nan
        return result

    def calculate_weight_7day_avg(self, df: pd.DataFrame) -> pd.Series:
        """体重7日滚动均值

        异常值检测：
        - 单日变化 > 5kg → 异常值
        - < 30kg 或 > 300kg → 异常值
        - 排除未佩戴日
        """
        if "body_mass_kg" not in df.columns:
            return pd.Series(index=df.index, dtype=float)

        weight = self._exclude_not_worn(df["body_mass_kg"], df)

        weight_change = weight.diff().abs()
        weight.loc[weight_change > self.weight_max_daily_change] = np.nan
        weight.loc[(weight < self.weight_min_value) | (weight > self.weight_max_value)] = np.nan

        return weight.rolling(window=self.window_days, min_periods=self.min_valid_days).mean()

    def calculate_steps_7day_avg(self, df: pd.DataFrame) -> pd.Series:
        """步数7日滚动均值

        异常值检测：
        - < 0 或 > 100,000 → 异常值
        - 排除未佩戴日
        """
        if "steps" not in df.columns:
            return pd.Series(index=df.index, dtype=float)

        steps = self._exclude_not_worn(df["steps"], df)
        steps.loc[(steps < self.steps_min_value) | (steps > self.steps_max_value)] = np.nan

        return steps.rolling(window=self.window_days, min_periods=self.min_valid_days).mean()

    def calculate_exercise_weekly_total(self, df: pd.DataFrame) -> pd.Series:
        """每周运动分钟数（7日滚动总和）"""
        if "exercise_minutes" not in df.columns:
            return pd.Series(index=df.index, dtype=float)

        exercise = self._exclude_not_worn(df["exercise_minutes"], df)
        exercise.loc[
            (exercise < self.exercise_min_value) | (exercise > self.exercise_max_value)
        ] = np.nan

        return exercise.rolling(window=self.window_days, min_periods=self.min_valid_days).sum()

    def calculate_resting_hr_7day_avg(self, df: pd.DataFrame) -> pd.Series:
        """静息心率7日滚动均值

        异常值检测：
        - < 40 或 > 120 bpm → 异常值
        - 排除未佩戴日
        """
        if "resting_hr_bpm" not in df.columns:
            return pd.Series(index=df.index, dtype=float)

        hr = self._exclude_not_worn(df["resting_hr_bpm"], df)
        hr.loc[(hr < self.hr_min_value) | (hr > self.hr_max_value)] = np.nan

        return hr.rolling(window=self.window_days, min_periods=3).mean()

    def calculate_hrv_7day_avg(self, df: pd.DataFrame) -> pd.Series:
        """HRV 7日滚动均值

        异常值检测：
        - < 10ms 或 > 200ms → 异常值
        - 排除未佩戴日
        """
        if "hrv_ms" not in df.columns:
            return pd.Series(index=df.index, dtype=float)

        hrv = self._exclude_not_worn(df["hrv_ms"], df)
        hrv.loc[(hrv < self.hrv_min_value) | (hrv > self.hrv_max_value)] = np.nan

        return hrv.rolling(window=self.window_days, min_periods=3).mean()

    def calculate_low_activity_days_7day(self, df: pd.DataFrame) -> pd.Series:
        """7日内低活动日数量

        使用 is_low_activity_day 字段（如果存在），
        否则回退到 steps < 1000 且已佩戴 的判断。
        """
        if "is_low_activity_day" in df.columns:
            is_low = df["is_low_activity_day"].astype(float)
        elif "steps" in df.columns:
            is_worn = (
                df["wear_status"] != "not_worn"
                if "wear_status" in df.columns
                else pd.Series(True, index=df.index)
            )
            is_low = ((df["steps"] < 1000) & is_worn).astype(float)
        else:
            return pd.Series(index=df.index, dtype=int)

        return is_low.rolling(window=self.window_days, min_periods=self.min_valid_days).sum().astype('Int64')

    def get_rolling_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取滚动指标的统计摘要"""
        summary = {}

        for col in ["weight_7day_avg", "steps_7day_avg", "exercise_weekly_total",
                     "resting_hr_7day_avg", "hrv_7day_avg", "low_activity_days_7day"]:
            if col in df.columns:
                data = df[col].dropna()
                if not data.empty:
                    summary[col] = {
                        "mean": float(data.mean()),
                        "min": float(data.min()),
                        "max": float(data.max()),
                    }

        return summary
