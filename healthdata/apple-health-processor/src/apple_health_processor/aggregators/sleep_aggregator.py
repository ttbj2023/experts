"""睡眠数据聚合器

处理睡眠数据，按起床日期归属（跨天睡眠处理）。
支持去重、深度睡眠追踪。
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import pandas as pd

logger = logging.getLogger(__name__)


class SleepAggregator:
    """睡眠数据聚合器

    处理 Apple Health 睡眠数据：
    - 按起床日期归属（而非入睡日期）
    - 自动去重（同一时间段的重复记录）
    - 追踪深度睡眠时间
    """

    SLEEP_ANALYSIS_TYPES = {
        "HKCategoryTypeIdentifierSleepAnalysis",
    }

    SLEEP_STATE_AWAKE = 0
    SLEEP_STATE_ASLEEP = 1
    SLEEP_STATE_IN_BED = 2
    SLEEP_STATE_DEEP = 3

    def __init__(self):
        self.sleep_records = []

    def add_sleep_record(self, record: Dict[str, Any]) -> None:
        """添加睡眠分析记录"""
        record_type = record.get("type")
        if record_type not in self.SLEEP_ANALYSIS_TYPES:
            return

        value_str = record.get("value")
        if value_str is None:
            return

        sleep_state = None
        if isinstance(value_str, int):
            sleep_state = value_str
        elif isinstance(value_str, str):
            sleep_state_map = {
                "HKCategoryValueSleepAnalysisInBed": self.SLEEP_STATE_IN_BED,
                "HKCategoryValueSleepAnalysisAsleep": self.SLEEP_STATE_ASLEEP,
                "HKCategoryValueSleepAnalysisAsleepCore": self.SLEEP_STATE_ASLEEP,
                "HKCategoryValueSleepAnalysisAsleepDeep": self.SLEEP_STATE_DEEP,
                "HKCategoryValueSleepAnalysisAsleepREM": self.SLEEP_STATE_ASLEEP,
                "HKCategoryValueSleepAnalysisAsleepUnspecified": self.SLEEP_STATE_ASLEEP,
                "HKCategoryValueSleepAnalysisAwake": self.SLEEP_STATE_AWAKE,
            }
            sleep_state = sleep_state_map.get(value_str)
        else:
            try:
                sleep_state = int(value_str)
            except (ValueError, TypeError):
                pass

        if sleep_state is None:
            return

        start_date = record.get("startDate")
        end_date = record.get("endDate")

        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            return

        duration_minutes = (end_date - start_date).total_seconds() / 60.0

        self.sleep_records.append({
            "start": start_date,
            "end": end_date,
            "duration_minutes": duration_minutes,
            "sleep_state": sleep_state,
            "source": record.get("sourceName"),
        })

    def _deduplicate_records(self, records: List[Dict]) -> List[Dict]:
        """去重：移除同一时间段+状态的重复记录，过滤无效时长

        Sleepace 等设备会在不同 creationDate 重复上报相同数据，
        按 (start, end, sleep_state) 去重消除此问题。
        同时过滤 duration_minutes <= 0 的无效记录。

        Args:
            records: 原始睡眠记录列表

        Returns:
            去重后的记录列表（按 start 排序）
        """
        seen = set()
        deduped = []
        for rec in records:
            if rec["duration_minutes"] <= 0:
                continue
            key = (rec["start"], rec["end"], rec["sleep_state"])
            if key not in seen:
                seen.add(key)
                deduped.append(rec)

        deduped.sort(key=lambda x: x["start"])
        return deduped

    def _group_sleep_periods(self) -> Dict[Any, List[Dict[str, Any]]]:
        """将睡眠记录按睡眠周期分组

        将连续的睡眠记录（间隔 ≤ 60 分钟）合并为一个睡眠周期，
        并按起床日期归属。
        """
        if not self.sleep_records:
            return {}

        sorted_records = self._deduplicate_records(self.sleep_records)

        if not sorted_records:
            return {}

        sleep_periods = []
        current_period = None

        for record in sorted_records:
            if current_period is None:
                current_period = {
                    "period_start": record["start"],
                    "period_end": record["end"],
                    "records": [record],
                    "total_bed_minutes": record["duration_minutes"],
                    "total_asleep_minutes": 0.0,
                    "total_deep_minutes": 0.0,
                    "total_awake_minutes": 0.0,
                }
                self._accumulate_state(current_period, record)
            else:
                time_gap = (record["start"] - current_period["period_end"]).total_seconds() / 60.0

                if time_gap <= 60:
                    current_period["period_end"] = max(
                        current_period["period_end"], record["end"]
                    )
                    current_period["records"].append(record)
                    current_period["total_bed_minutes"] += record["duration_minutes"]
                    self._accumulate_state(current_period, record)
                else:
                    sleep_periods.append(current_period)
                    current_period = {
                        "period_start": record["start"],
                        "period_end": record["end"],
                        "records": [record],
                        "total_bed_minutes": record["duration_minutes"],
                        "total_asleep_minutes": 0.0,
                        "total_deep_minutes": 0.0,
                        "total_awake_minutes": 0.0,
                    }
                    self._accumulate_state(current_period, record)

        if current_period:
            sleep_periods.append(current_period)

        periods_by_date = defaultdict(list)
        for period in sleep_periods:
            wake_time = period["period_end"]
            if wake_time.tzinfo is not None:
                wake_date = wake_time.astimezone().date()
            else:
                wake_date = wake_time.date()
            periods_by_date[wake_date].append(period)

        return periods_by_date

    def _accumulate_state(self, period: Dict, record: Dict) -> None:
        """根据睡眠状态累加对应计数器

        注意：deep sleep 同时计入 asleep_minutes（深度睡眠是入睡的子集）。
        """
        state = record["sleep_state"]
        duration = record["duration_minutes"]

        if state == self.SLEEP_STATE_ASLEEP:
            period["total_asleep_minutes"] += duration
        elif state == self.SLEEP_STATE_DEEP:
            period["total_asleep_minutes"] += duration
            period["total_deep_minutes"] += duration
        elif state == self.SLEEP_STATE_AWAKE:
            period["total_awake_minutes"] += duration

    def _select_primary_sleep_period(self, periods: List[Dict]) -> Optional[Dict]:
        """选择主要睡眠周期（持续时间最长的）"""
        if not periods:
            return None
        return max(periods, key=lambda x: x["total_bed_minutes"])

    def get_sleep_summary(self) -> pd.DataFrame:
        """获取睡眠汇总数据"""
        periods_by_date = self._group_sleep_periods()

        if not periods_by_date:
            logger.warning("没有找到有效的睡眠数据")
            return pd.DataFrame()

        sleep_rows = []

        for date, periods in sorted(periods_by_date.items()):
            primary_period = self._select_primary_sleep_period(periods)
            if not primary_period:
                continue

            bed_time = primary_period["period_start"]
            wake_time = primary_period["period_end"]

            in_bed_minutes = primary_period["total_bed_minutes"]
            asleep_minutes = primary_period["total_asleep_minutes"]
            deep_minutes = primary_period["total_deep_minutes"]
            awake_minutes = primary_period["total_awake_minutes"]

            if in_bed_minutes > 0:
                sleep_efficiency = (asleep_minutes / in_bed_minutes) * 100
            else:
                sleep_efficiency = None

            bed_time_hour = bed_time.hour + bed_time.minute / 60 if isinstance(bed_time, datetime) else None
            wake_time_hour = wake_time.hour + wake_time.minute / 60 if isinstance(wake_time, datetime) else None

            row = {
                "date": date,
                "bed_time": bed_time,
                "wake_time": wake_time,
                "in_bed_minutes": in_bed_minutes,
                "asleep_minutes": asleep_minutes,
                "deep_sleep_minutes": deep_minutes,
                "awake_minutes": awake_minutes,
                "sleep_efficiency": sleep_efficiency,
                "bed_time_hour": bed_time_hour,
                "wake_time_hour": wake_time_hour,
                "sleep_duration_hours": asleep_minutes / 60 if asleep_minutes else None,
                "time_in_bed_hours": in_bed_minutes / 60 if in_bed_minutes else None,
            }

            sleep_rows.append(row)

        df = pd.DataFrame(sleep_rows)
        if not df.empty:
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)

        return df

    def get_summary_statistics(self) -> Dict[str, Any]:
        """获取汇总统计信息"""
        if not self.sleep_records:
            return {"total_sleep_records": 0, "total_nights": 0}

        periods_by_date = self._group_sleep_periods()

        return {
            "total_sleep_records": len(self.sleep_records),
            "total_nights": len(periods_by_date),
        }
