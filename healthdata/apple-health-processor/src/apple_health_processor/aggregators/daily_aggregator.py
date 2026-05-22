"""每日数据聚合器

按日期聚合健康数据，包括步数累加、能量累加、体重晨起值选择等。
"""

import logging
from collections import defaultdict
from datetime import datetime, time, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class DailyAggregator:
    """每日健康数据聚合器

    按日期聚合各种健康指标：
    - 步数、能量、距离：累加
    - 体重：选择晨起值（6-10点首个测量值）
    - 心率、HRV、VO2 Max：平均值
    """

    # 晨起时间段：6:00-10:00
    MORNING_HOUR_START = 6
    MORNING_HOUR_END = 10

    def __init__(self):
        """初始化聚合器"""
        self.daily_data = defaultdict(lambda: defaultdict(list))
        # 分别存储不同来源的exercise数据，优先级：summary > granular
        self.exercise_data_sources = defaultdict(dict)

    # 需要按日拆分的累加类型
    CROSS_DAY_SPLIT_TYPES = {
        "HKQuantityTypeIdentifierStepCount",
        "HKQuantityTypeIdentifierActiveEnergyBurned",
        "HKQuantityTypeIdentifierBasalEnergyBurned",
        "HKQuantityTypeIdentifierDistanceWalkingRunning",
    }

    def _to_local_date(self, dt: datetime) -> Any:
        """将 datetime 转换为本地日期"""
        if dt.tzinfo is not None:
            return dt.astimezone().date()
        return dt.date()

    def _to_local_dt(self, dt: datetime) -> datetime:
        """将 datetime 转换为本地时间（去除时区信息的偏移）"""
        if dt.tzinfo is not None:
            return dt.astimezone()
        return dt

    def _split_cross_day_value(
        self, start_date: datetime, end_date: datetime, value: float
    ) -> List[Tuple[Any, float]]:
        """将跨天记录按每日秒数占比拆分

        对于 startDate 和 endDate 不在同一天的累加型记录，
        按每天实际覆盖的秒数比例分配 value。

        Args:
            start_date: 记录开始时间
            end_date: 记录结束时间
            value: 记录值

        Returns:
            List of (date, proportioned_value) 元组
        """
        local_start = self._to_local_dt(start_date)
        local_end = self._to_local_dt(end_date)

        start_day = local_start.date()
        end_day = local_end.date()

        if start_day == end_day:
            return [(start_day, value)]

        total_seconds = (local_end - local_start).total_seconds()
        if total_seconds <= 0:
            return [(start_day, value)]

        result = []
        current_day = start_day

        while current_day <= end_day:
            day_start = datetime(
                current_day.year, current_day.month, current_day.day,
                tzinfo=local_start.tzinfo
            )
            next_day = current_day + timedelta(days=1)
            day_end = datetime(
                next_day.year, next_day.month, next_day.day,
                tzinfo=local_start.tzinfo
            )

            # 当前天的有效区间
            seg_start = max(local_start, day_start)
            seg_end = min(local_end, day_end)

            seg_seconds = (seg_end - seg_start).total_seconds()
            if seg_seconds > 0:
                proportion = seg_seconds / total_seconds
                result.append((current_day, value * proportion))

            current_day = next_day

        return result

    def add_record(self, record: Dict[str, Any]) -> None:
        """添加单条健康记录

        对于累加类型（步数、能量、距离），如果记录跨天则按时间比例拆分。
        其他类型（晨起值、均值型）不做拆分。

        Args:
            record: 健康记录字典，包含 type, value, startDate 等字段
        """
        record_type = record.get("type")
        if not record_type:
            return

        value_str = record.get("value")
        if value_str is None:
            return

        try:
            value = float(value_str)
        except (ValueError, TypeError):
            return

        start_date = record.get("startDate")
        if not isinstance(start_date, datetime):
            return

        end_date = record.get("endDate")
        local_start = self._to_local_date(start_date)

        # 累加类型：检查是否跨天，需要按日拆分
        if record_type in self.CROSS_DAY_SPLIT_TYPES and isinstance(end_date, datetime):
            local_end = self._to_local_date(end_date)
            if local_start != local_end:
                for day, day_value in self._split_cross_day_value(start_date, end_date, value):
                    self._aggregate_by_type(day, record_type, day_value, start_date, record)
                return

        self._aggregate_by_type(local_start, record_type, value, start_date, record)

    def _aggregate_by_type(
        self,
        date: Any,
        record_type: str,
        value: float,
        datetime_obj: datetime,
        record: Dict[str, Any]
    ) -> None:
        """根据记录类型进行聚合

        Args:
            date: 日期对象
            record_type: HealthKit 记录类型
            value: 数值
            datetime_obj: 完整日期时间对象
            record: 原始记录
        """
        # 步数、能量、距离 - 累加类型
        if record_type == "HKQuantityTypeIdentifierStepCount":
            self.daily_data[date]["steps"].append(value)
        elif record_type == "HKQuantityTypeIdentifierActiveEnergyBurned":
            self.daily_data[date]["active_energy_kcal"].append(value)
        elif record_type == "HKQuantityTypeIdentifierBasalEnergyBurned":
            self.daily_data[date]["basal_energy_kcal"].append(value)
        elif record_type == "HKQuantityTypeIdentifierDistanceWalkingRunning":
            self.daily_data[date]["distance_km"].append(value)  # XML中单位已经是km
        elif record_type == "HKQuantityTypeIdentifierAppleExerciseTime":
            # 存储细粒度记录到exercise_data_sources
            date_key = date
            if 'granular' not in self.exercise_data_sources[date_key]:
                self.exercise_data_sources[date_key]['granular'] = []
            self.exercise_data_sources[date_key]['granular'].append(value)

        # 体重 - 选择晨起值
        elif record_type == "HKQuantityTypeIdentifierBodyMass":
            # 存储为 (时间, 体重) 元组，以便后续筛选晨起值
            self.daily_data[date]["body_mass_records"].append((datetime_obj, value))

        # 心率、HRV、VO2 Max - 平均类型
        elif record_type == "HKQuantityTypeIdentifierRestingHeartRate":
            self.daily_data[date]["resting_hr_bpm"].append(value)
        elif record_type == "HKQuantityTypeIdentifierHeartRateVariabilitySDNN":
            self.daily_data[date]["hrv_ms"].append(value)
        elif record_type == "HKQuantityTypeIdentifierVO2Max":
            self.daily_data[date]["vo2_max"].append(value)

        # 体脂率 - 晨起值（XML 中为小数形式 0-1，需 × 100 转为百分比）
        elif record_type == "HKQuantityTypeIdentifierBodyFatPercentage":
            self.daily_data[date]["body_fat_records"].append((datetime_obj, value * 100))

        # 去脂体重 - 晨起值
        elif record_type == "HKQuantityTypeIdentifierLeanBodyMass":
            self.daily_data[date]["muscle_mass_records"].append((datetime_obj, value))

    def _get_morning_weight(self, weight_records: List[tuple]) -> Optional[float]:
        """获取晨起体重（6-10点首个测量值）

        Args:
            weight_records: [(datetime, weight), ...] 列表

        Returns:
            Optional[float]: 晨起体重，如果没有则返回 None
        """
        if not weight_records:
            return None

        # 筛选晨起时间段（6:00-10:00）的记录
        morning_records = [
            (dt, weight) for dt, weight in weight_records
            if self.MORNING_HOUR_START <= dt.hour < self.MORNING_HOUR_END
        ]

        if not morning_records:
            sorted_records = sorted(weight_records, key=lambda x: x[0])
            return sorted_records[0][1]

        # 返回晨起时间段的首个值
        morning_records.sort(key=lambda x: x[0])  # 按时间排序
        return morning_records[0][1]

    def add_activity_summary(self, summary: Dict[str, Any]) -> None:
        """添加活动汇总数据

        Args:
            summary: 活动汇总字典，包含 date, exercise_minutes, stand_hours 等
        """
        date = summary.get("date")
        if date is None:
            return

        if isinstance(date, datetime):
            date_key = date.date()
        else:
            date_key = date

        # 活动汇总的数据是已经聚合好的，直接使用（优先级最高）
        exercise_minutes = summary.get("exercise_minutes")
        if exercise_minutes is not None:
            self.exercise_data_sources[date_key]['summary'] = exercise_minutes

        stand_hours = summary.get("stand_hours")
        if stand_hours is not None:
            self.daily_data[date_key]["stand_hours"].append(stand_hours)

        active_energy = summary.get("active_energy_kcal")
        if active_energy is not None:
            self.daily_data[date_key]["active_energy_kcal"].append(active_energy)

    def _resolve_exercise_minutes(self, date: Any) -> float:
        """智能解析运动时间，优先使用ActivitySummary数据

        数据来源优先级：
        1. ActivitySummary 汇总数据（最准确）
        2. 细粒度记录累加（仅在没有汇总数据时使用）

        Args:
            date: 日期对象

        Returns:
            float: 运动时间（分钟）
        """
        if date not in self.exercise_data_sources:
            return 0

        sources = self.exercise_data_sources[date]

        # 优先级1: ActivitySummary 汇总数据
        if 'summary' in sources and sources['summary'] is not None:
            return sources['summary']

        # 优先级2: 细粒度记录累加
        if 'granular' in sources and sources['granular']:
            return sum(sources['granular'])

        return 0

    def get_daily_summary(self) -> pd.DataFrame:
        """获取每日汇总数据

        Returns:
            pd.DataFrame: 包含每日汇总数据的 DataFrame
        """
        daily_rows = []

        for date, metrics in sorted(self.daily_data.items()):
            row = {"date": date}

            # 步数、能量、距离 - 累加
            row["steps"] = sum(metrics.get("steps", [0]))
            row["active_energy_kcal"] = sum(metrics.get("active_energy_kcal", [0]))
            row["basal_energy_kcal"] = sum(metrics.get("basal_energy_kcal", [0]))
            row["distance_km"] = sum(metrics.get("distance_km", [0]))

            # 运动时间 - 使用智能解析（优先ActivitySummary汇总数据）
            row["exercise_minutes"] = self._resolve_exercise_minutes(date)

            stand_values = metrics.get("stand_hours", [])
            row["stand_hours"] = max(stand_values) if stand_values else 0

            # 体重 - 晨起值
            weight_records = metrics.get("body_mass_records", [])
            row["body_mass_kg"] = self._get_morning_weight(weight_records)

            # 心率、HRV、VO2 Max - 平均值
            resting_hr = metrics.get("resting_hr_bpm", [])
            row["resting_hr_bpm"] = sum(resting_hr) / len(resting_hr) if resting_hr else None

            hrv_ms = metrics.get("hrv_ms", [])
            row["hrv_ms"] = sum(hrv_ms) / len(hrv_ms) if hrv_ms else None

            vo2_max = metrics.get("vo2_max", [])
            row["vo2_max"] = sum(vo2_max) / len(vo2_max) if vo2_max else None

            # 体脂率、去脂体重 - 晨起值（与体重相同的选取逻辑）
            body_fat_records = metrics.get("body_fat_records", [])
            row["body_fat_pct"] = self._get_morning_weight(body_fat_records)

            muscle_mass_records = metrics.get("muscle_mass_records", [])
            row["muscle_mass_kg"] = self._get_morning_weight(muscle_mass_records)

            daily_rows.append(row)

        df = pd.DataFrame(daily_rows)
        if not df.empty:
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)

        return df

    def get_summary_statistics(self) -> Dict[str, Any]:
        """获取汇总统计信息

        Returns:
            Dict: 统计信息字典
        """
        if not self.daily_data:
            return {
                "total_days": 0,
                "date_range": None,
            }

        dates = sorted(self.daily_data.keys())
        return {
            "total_days": len(dates),
            "date_range": (dates[0], dates[-1]),
        }
