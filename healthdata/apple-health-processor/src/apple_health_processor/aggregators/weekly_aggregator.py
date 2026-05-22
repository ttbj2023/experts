"""每周数据聚合器

基于每日数据使用 pandas resample 生成每周汇总。
仅统计已佩戴设备的天数，有效天数不足 4 天时不计算日均值。
"""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class WeeklyAggregator:
    """每周健康数据聚合器

    规则：
    - 仅统计 wear_status == "worn" 的天数
    - 有效天数 < 4 时，日均值和身体指标均值设为 None
    - 累加总值（steps_total 等）在有效天数 > 0 时仍然计算
    """

    MIN_VALID_DAYS = 4

    def __init__(self):
        self.weekly_data = None

    def aggregate_from_daily(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        """从每日数据生成每周汇总

        Args:
            daily_df: 每日汇总数据 DataFrame，可含 wear_status 列

        Returns:
            pd.DataFrame: 每周汇总数据 DataFrame
        """
        if daily_df.empty:
            logger.warning("每日数据为空，无法生成每周汇总")
            return pd.DataFrame()

        df = daily_df.copy()

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # 过滤未佩戴天
        if "wear_status" in df.columns:
            df = df[df["wear_status"] == "worn"].copy()
            if df.empty:
                logger.warning("没有已佩戴天数据，无法生成每周汇总")
                return pd.DataFrame()

        weekly_resampled = df.resample("W-MON", label="left", closed="left")

        weekly_rows = []
        for week_start, week_data in weekly_resampled:
            if week_data.empty:
                continue

            days_in_week = len(week_data)

            row = {"week_start": week_start.date()}

            # 累加指标
            row["steps_total"] = week_data["steps"].sum()
            row["active_energy_kcal_total"] = week_data["active_energy_kcal"].sum()
            row["basal_energy_kcal_total"] = week_data["basal_energy_kcal"].sum()
            row["distance_km_total"] = week_data["distance_km"].sum()
            row["exercise_minutes_total"] = week_data["exercise_minutes"].sum()
            row["stand_hours_total"] = week_data["stand_hours"].sum()

            # 均值指标
            body_mass = week_data["body_mass_kg"].dropna()
            row["body_mass_kg_avg"] = body_mass.mean() if not body_mass.empty else None

            resting_hr = week_data["resting_hr_bpm"].dropna()
            row["resting_hr_bpm_avg"] = resting_hr.mean() if not resting_hr.empty else None

            hrv_ms = week_data["hrv_ms"].dropna()
            row["hrv_ms_avg"] = hrv_ms.mean() if not hrv_ms.empty else None

            vo2_max = week_data["vo2_max"].dropna()
            row["vo2_max_avg"] = vo2_max.mean() if not vo2_max.empty else None

            # 有效天数
            row["days_in_week"] = days_in_week

            # 日均值：有效天数 >= 4 才计算
            if days_in_week >= self.MIN_VALID_DAYS:
                row["steps_daily_avg"] = row["steps_total"] / days_in_week
                row["active_energy_kcal_daily_avg"] = row["active_energy_kcal_total"] / days_in_week
                row["distance_daily_avg"] = row["distance_km_total"] / days_in_week
            else:
                row["steps_daily_avg"] = None
                row["active_energy_kcal_daily_avg"] = None
                row["distance_daily_avg"] = None

            weekly_rows.append(row)

        weekly_df = pd.DataFrame(weekly_rows)
        if not weekly_df.empty:
            weekly_df.set_index("week_start", inplace=True)

        self.weekly_data = weekly_df
        return weekly_df

    def get_summary_statistics(self) -> dict:
        """获取汇总统计信息"""
        if self.weekly_data is None or self.weekly_data.empty:
            return {"total_weeks": 0, "date_range": None}

        start_idx = self.weekly_data.index[0]
        end_idx = self.weekly_data.index[-1]

        start_date = start_idx.date() if hasattr(start_idx, "date") else start_idx
        end_date = end_idx.date() if hasattr(end_idx, "date") else end_idx

        return {"total_weeks": len(self.weekly_data), "date_range": (start_date, end_date)}
