"""XML 流式解析器

使用 lxml.etree.iterparse 实现增量解析，避免内存问题。
处理 Apple Health 导出的 XML 数据文件。
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, Optional
from dateutil import parser as date_parser
from lxml import etree

logger = logging.getLogger(__name__)


class XMLStreamParser:
    """Apple Health XML 流式解析器

    使用 iterparse 增量处理大型 XML 文件，避免内存占用问题。
    处理完元素后立即清理，保持内存使用恒定。
    """

    # 需要处理的 XML 元素类型
    TARGET_ELEMENTS = {
        "Record",      # 健康数据记录
        "Workout",     # 运动记录
        "ActivitySummary",  # 活动汇总
        "MetadataEntry",    # 元数据条目
        "Correlation",      # 关联数据
        "WorkoutRoute",     # 运动路线
        "ExportDate",       # 导出日期
    }

    def __init__(self, xml_path: str | Path):
        """初始化解析器

        Args:
            xml_path: Apple Health XML 文件路径
        """
        self.xml_path = Path(xml_path)
        if not self.xml_path.exists():
            raise FileNotFoundError(f"XML 文件不存在: {xml_path}")

        self.export_date: Optional[datetime] = None

    def iterparse(self, tag: str) -> Iterator[etree._Element]:
        """使用 iterparse 增量解析 XML

        Args:
            tag: 要提取的标签名

        Yields:
            etree._Element: 解析出的 XML 元素
        """
        context = etree.iterparse(
            str(self.xml_path),
            events=("end",),
            tag=tag,
            remove_blank_text=True,
            remove_comments=True,
            remove_pis=True,
        )

        for event, elem in context:
            yield elem
            # 及时清理已处理的元素及其兄弟节点
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    def _parse_datetime(self, date_str: str) -> datetime:
        """解析日期时间字符串，处理时区

        Args:
            date_str: 日期时间字符串，可能包含时区信息（如 +0800）

        Returns:
            datetime: 解析后的 datetime 对象
        """
        if not date_str:
            return datetime.now(timezone.utc)

        try:
            # Apple Health 格式: "2024-05-21 08:30:00 +0800"
            # 处理时区格式
            dt = date_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception as e:
            logger.warning(f"无法解析日期时间 '{date_str}': {e}")
            return datetime.now(timezone.utc)

    def iter_records(
        self, record_type: Optional[str] = None
    ) -> Generator[Dict[str, str | float | int | datetime], None, None]:
        """迭代健康数据记录

        Args:
            record_type: 可选，只返回特定类型的记录（如 HKQuantityTypeIdentifierStepCount）

        Yields:
            Dict: 包含记录数据的字典
        """
        for elem in self.iterparse("Record"):
            # 跳过导出日期
            if elem.get("type") == "HKQuantityTypeIdentifierExportDate":
                self.export_date = self._parse_datetime(elem.get("startDate") or elem.get("creationDate"))
                continue

            # 可选过滤记录类型
            if record_type and elem.get("type") != record_type:
                continue

            yield {
                "type": elem.get("type"),
                "unit": elem.get("unit"),
                "value": elem.get("value"),
                "startDate": self._parse_datetime(elem.get("startDate")),
                "endDate": self._parse_datetime(elem.get("endDate")),
                "sourceName": elem.get("sourceName"),
                "device": elem.get("device"),
                "creationDate": self._parse_datetime(elem.get("creationDate")),
            }

    def _extract_workout_heart_rate(self, elem) -> Dict[str, Optional[float]]:
        """从 Workout 子元素中提取心率统计数据

        Apple Health XML 中运动心率数据格式:
        <WorkoutStatistics type="HKQuantityTypeIdentifierHeartRate"
                           average="96.562" minimum="77" maximum="116" unit="count/min"/>

        Args:
            elem: Workout XML 元素

        Returns:
            Dict: 包含 heart_rate_avg 和 heart_rate_max 的字典
        """
        heart_rate_avg = None
        heart_rate_max = None

        for stat_elem in elem.iterchildren("WorkoutStatistics"):
            stat_type = stat_elem.get("type", "")
            if "HeartRate" not in stat_type:
                continue

            avg_str = stat_elem.get("average")
            if avg_str:
                try:
                    heart_rate_avg = float(avg_str)
                except (ValueError, TypeError):
                    pass

            max_str = stat_elem.get("maximum")
            if max_str:
                try:
                    heart_rate_max = float(max_str)
                except (ValueError, TypeError):
                    pass

            break

        return {"heart_rate_avg": heart_rate_avg, "heart_rate_max": heart_rate_max}

    def iter_workouts(self) -> Generator[Dict[str, Any], None, None]:
        """迭代运动记录

        Yields:
            Dict: 包含运动数据的字典
        """
        for elem in self.iterparse("Workout"):
            workout_type = elem.get("workoutActivityType")
            # 提取活动类型名称
            if workout_type and workout_type.startswith("HKWorkoutActivityType"):
                activity_name = workout_type.replace("HKWorkoutActivityType", "")
            else:
                activity_name = workout_type or "Unknown"

            duration = elem.get("duration")
            try:
                duration_seconds = float(duration) if duration else 0.0
            except ValueError:
                duration_seconds = 0.0

            distance = elem.get("totalDistance")
            try:
                distance_km = float(distance) / 1000.0 if distance else 0.0
            except ValueError:
                distance_km = 0.0

            energy = elem.get("totalEnergyBurned")
            try:
                energy_kcal = float(energy) if energy else 0.0
            except ValueError:
                energy_kcal = 0.0

            hr_stats = self._extract_workout_heart_rate(elem)

            yield {
                "type": activity_name,
                "duration_seconds": duration_seconds,
                "distance_km": distance_km,
                "energy_kcal": energy_kcal,
                "startDate": self._parse_datetime(elem.get("startDate")),
                "endDate": self._parse_datetime(elem.get("endDate")),
                "sourceName": elem.get("sourceName"),
                "device": elem.get("device"),
                "creationDate": self._parse_datetime(elem.get("creationDate")),
                "heart_rate_avg": hr_stats["heart_rate_avg"],
                "heart_rate_max": hr_stats["heart_rate_max"],
            }

    def iter_activity_summaries(self) -> Generator[Dict[str, Any], None, None]:
        """迭代活动汇总数据

        Yields:
            Dict: 包含活动汇总数据的字典
        """
        for elem in self.iterparse("ActivitySummary"):
            date_components = elem.get("dateComponents")
            if date_components:
                try:
                    # Apple Health 日期格式: "2024-05-21"
                    summary_date = datetime.strptime(date_components, "%Y-%m-%d")
                except ValueError:
                    summary_date = None
            else:
                summary_date = None

            active_energy = elem.get("activeEnergyBurned")
            try:
                active_energy_kcal = float(active_energy) if active_energy else 0.0
            except ValueError:
                active_energy_kcal = 0.0

            active_time = elem.get("appleExerciseTime")
            try:
                exercise_minutes = float(active_time) if active_time else 0.0
            except ValueError:
                exercise_minutes = 0.0

            stand_hours = elem.get("appleStandHours")
            try:
                stand_hours_count = float(stand_hours) if stand_hours else 0.0
            except ValueError:
                stand_hours_count = 0.0

            yield {
                "date": summary_date,
                "active_energy_kcal": active_energy_kcal,
                "exercise_minutes": exercise_minutes,
                "stand_hours": stand_hours_count,
            }

    def get_statistics(self) -> Dict[str, int]:
        """获取文件统计信息

        Returns:
            Dict: 包含各类记录数量的字典
        """
        stats = {
            "total_records": 0,
            "total_workouts": 0,
            "total_activity_summaries": 0,
        }

        # 快速统计各类记录数量
        for event, elem in etree.iterparse(str(self.xml_path), tag=("Record", "Workout", "ActivitySummary"), events=("end",)):
            tag = elem.tag
            if tag in stats:
                stats[f"total_{tag.lower()}s"] += 1
            elem.clear()

        return stats
