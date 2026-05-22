"""CSV 导出器

将处理后的健康数据导出为 CSV 文件。
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class CSVExporter:
    """CSV 数据导出器

    导出 4 个 CSV 文件：
    1. daily_health_summary.csv - 每日健康汇总
    2. weekly_health_summary.csv - 每周健康汇总
    3. workout_records.csv - 运动记录
    4. sleep_summary.csv - 睡眠汇总
    """

    def __init__(self, output_dir: str | Path = "output"):
        """初始化导出器

        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 导出统计信息
        self.export_stats = {
            "daily_rows": 0,
            "weekly_rows": 0,
            "workout_rows": 0,
            "sleep_rows": 0,
        }

    def export_daily_summary(self, daily_df: pd.DataFrame) -> Path:
        """导出每日健康汇总数据

        Args:
            daily_df: 每日汇总数据 DataFrame

        Returns:
            Path: 导出文件的路径
        """
        output_path = self.output_dir / "daily_health_summary.csv"

        if daily_df.empty:
            logger.warning("每日汇总数据为空，跳过导出")
            return output_path

        # 重置索引，使 date 成为一列
        export_df = daily_df.reset_index()

        # 格式化日期时间列
        export_df["date"] = export_df["date"].apply(
            lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else str(x)
        )

        # 导出为 CSV
        export_df.to_csv(output_path, index=False, encoding="utf-8")

        self.export_stats["daily_rows"] = len(export_df)
        logger.info(f"每日汇总数据已导出: {output_path} ({len(export_df)} 行)")

        return output_path

    def export_weekly_summary(self, weekly_df: pd.DataFrame) -> Path:
        """导出每周健康汇总数据

        Args:
            weekly_df: 每周汇总数据 DataFrame

        Returns:
            Path: 导出文件的路径
        """
        output_path = self.output_dir / "weekly_health_summary.csv"

        if weekly_df.empty:
            logger.warning("每周汇总数据为空，跳过导出")
            return output_path

        # 重置索引
        export_df = weekly_df.reset_index()

        # 格式化日期列
        export_df["week_start"] = export_df["week_start"].apply(
            lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else str(x)
        )

        # 导出为 CSV
        export_df.to_csv(output_path, index=False, encoding="utf-8")

        self.export_stats["weekly_rows"] = len(export_df)
        logger.info(f"每周汇总数据已导出: {output_path} ({len(export_df)} 行)")

        return output_path

    def export_workout_records(self, workouts: list[Dict[str, Any]]) -> Path:
        """导出运动记录数据

        Args:
            workouts: 运动记录列表

        Returns:
            Path: 导出文件的路径
        """
        output_path = self.output_dir / "workout_records.csv"

        if not workouts:
            logger.warning("运动记录数据为空，跳过导出")
            return output_path

        # 转换为 DataFrame
        workout_data = []

        for workout in workouts:
            start_date = workout.get("startDate")
            if start_date:
                date_str = start_date.strftime("%Y-%m-%d") if hasattr(start_date, "strftime") else str(start_date)
                start_time_str = start_date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(start_date, "strftime") else str(start_date)
            else:
                date_str = ""
                start_time_str = ""

            workout_data.append({
                "date": date_str,
                "workout_type": workout.get("type", "Unknown"),
                "duration_minutes": workout.get("duration_seconds", 0) / 60.0,
                "distance_km": workout.get("distance_km", 0),
                "energy_kcal": workout.get("energy_kcal", 0),
                "heart_rate_avg": workout.get("heart_rate_avg"),
                "heart_rate_max": workout.get("heart_rate_max"),
                "start_time": start_time_str,
                "source": workout.get("sourceName", ""),
            })

        df = pd.DataFrame(workout_data)

        # 导出为 CSV
        df.to_csv(output_path, index=False, encoding="utf-8")

        self.export_stats["workout_rows"] = len(df)
        logger.info(f"运动记录已导出: {output_path} ({len(df)} 行)")

        return output_path

    def export_sleep_summary(self, sleep_df: pd.DataFrame) -> Path:
        """导出睡眠汇总数据

        Args:
            sleep_df: 睡眠汇总数据 DataFrame

        Returns:
            Path: 导出文件的路径
        """
        output_path = self.output_dir / "sleep_summary.csv"

        if sleep_df.empty:
            logger.warning("睡眠汇总数据为空，跳过导出")
            return output_path

        # 重置索引
        export_df = sleep_df.reset_index()

        # 格式化日期时间列
        export_df["date"] = export_df["date"].apply(
            lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else str(x)
        )
        export_df["bed_time"] = export_df["bed_time"].apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if hasattr(x, "strftime") else str(x)
        )
        export_df["wake_time"] = export_df["wake_time"].apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if hasattr(x, "strftime") else str(x)
        )

        # 导出为 CSV
        export_df.to_csv(output_path, index=False, encoding="utf-8")

        self.export_stats["sleep_rows"] = len(export_df)
        logger.info(f"睡眠汇总已导出: {output_path} ({len(export_df)} 行)")

        return output_path

    def export_all(
        self,
        daily_df: pd.DataFrame,
        weekly_df: pd.DataFrame,
        workouts: list[Dict[str, Any]],
        sleep_df: pd.DataFrame,
    ) -> Dict[str, Path]:
        """导出所有数据

        Args:
            daily_df: 每日汇总数据
            weekly_df: 每周汇总数据
            workouts: 运动记录列表
            sleep_df: 睡眠汇总数据

        Returns:
            Dict[str, Path]: 各文件路径的字典
        """
        results = {}

        results["daily"] = self.export_daily_summary(daily_df)
        results["weekly"] = self.export_weekly_summary(weekly_df)
        results["workout"] = self.export_workout_records(workouts)
        results["sleep"] = self.export_sleep_summary(sleep_df)

        logger.info(f"所有数据已导出到: {self.output_dir}")
        self._print_summary()

        return results

    def _print_summary(self) -> None:
        """打印导出摘要信息"""
        logger.info("=" * 50)
        logger.info("导出摘要")
        logger.info("=" * 50)
        logger.info(f"每日汇总行数: {self.export_stats['daily_rows']}")
        logger.info(f"每周汇总行数: {self.export_stats['weekly_rows']}")
        logger.info(f"运动记录行数: {self.export_stats['workout_rows']}")
        logger.info(f"睡眠汇总行数: {self.export_stats['sleep_rows']}")
        logger.info("=" * 50)

    def get_export_stats(self) -> Dict[str, int]:
        """获取导出统计信息

        Returns:
            Dict: 统计信息字典
        """
        return self.export_stats.copy()
