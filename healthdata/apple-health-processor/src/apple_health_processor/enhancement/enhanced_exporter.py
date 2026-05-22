"""增强数据导出器

导出增强数据和统计分析报告。
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)


class EnhancedExporter:
    """增强数据导出器

    导出以下内容：
    1. 增强的CSV数据文件
    2. 统计分析报告
    3. 质量分析报告
    """

    def __init__(self):
        self.export_stats = {}

    def export_enhanced_data(
        self,
        enhanced_daily: pd.DataFrame,
        enhanced_weekly: pd.DataFrame,
        statistics: Dict[str, Dict[str, Any]],
        output_dir: Path
    ) -> Dict[str, str]:
        """导出增强数据和统计报告"""
        results = {}

        output_dir.mkdir(parents=True, exist_ok=True)

        daily_path = self._export_enhanced_csv(enhanced_daily, output_dir)
        results["daily_enhanced"] = str(daily_path)

        if enhanced_weekly is not None and not enhanced_weekly.empty:
            weekly_path = self._export_enhanced_csv(
                enhanced_weekly, output_dir, suffix="weekly_enhanced"
            )
            results["weekly_enhanced"] = str(weekly_path)

        stats_path = self._export_statistics_report(statistics, output_dir)
        results["statistics_report"] = str(stats_path)

        quality_path = self._export_quality_report(enhanced_daily, output_dir)
        results["quality_report"] = str(quality_path)

        logger.info(f"所有增强数据已导出到: {output_dir}")

        return results

    def _export_enhanced_csv(
        self,
        df: pd.DataFrame,
        output_dir: Path,
        suffix: str = "daily_health_summary_enhanced"
    ) -> Path:
        """导出增强的CSV文件"""
        output_path = output_dir / f"{suffix}.csv"

        export_df = df.reset_index()

        if "date" in export_df.columns:
            export_df["date"] = export_df["date"].apply(
                lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else str(x)
            )

        export_df.to_csv(output_path, index=False, encoding="utf-8")

        logger.info(f"增强CSV已导出: {output_path} ({len(export_df)} 行)")

        return output_path

    def _export_statistics_report(
        self,
        statistics: Dict[str, Dict[str, Any]],
        output_dir: Path
    ) -> Path:
        """导出统计报告"""
        output_path = output_dir / "statistics_report.txt"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("Apple Health 数据统计报告\n")
            f.write("=" * 70 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for mode, stats in statistics.items():
                f.write("-" * 70 + "\n")
                f.write(f"统计模式: {mode}\n")
                f.write("-" * 70 + "\n")

                self._write_statistics(f, stats)
                f.write("\n")

        logger.info(f"统计报告已导出: {output_path}")

        return output_path

    def _write_statistics(self, f, stats: Dict[str, Any]) -> None:
        """写入统计信息到文件"""
        f.write(f"天数: {stats['days_count']}\n")

        f.write(f"\n步数统计:\n")
        f.write(f"  总计: {stats['steps_total']:,} 步\n")
        f.write(f"  平均: {stats['steps_avg']:,.0f} 步/天\n")
        f.write(f"  最小: {stats['steps_min']:,} 步\n")
        f.write(f"  最大: {stats['steps_max']:,} 步\n")
        f.write(f"  标准差: {stats['steps_std']:,.0f}\n")

        f.write(f"\n能量统计:\n")
        f.write(f"  活动能量总计: {stats['active_energy_total']:,.0f} kcal\n")
        f.write(f"  活动能量平均: {stats['active_energy_avg']:,.0f} kcal/天\n")
        f.write(f"  基础能量总计: {stats['basal_energy_total']:,.0f} kcal\n")
        f.write(f"  基础能量平均: {stats['basal_energy_avg']:,.0f} kcal/天\n")

        f.write(f"\n距离统计:\n")
        f.write(f"  总计: {stats['distance_total']:.2f} km\n")
        f.write(f"  平均: {stats['distance_avg']:.2f} km/天\n")

        f.write(f"\n运动时间统计:\n")
        f.write(f"  总计: {stats['exercise_minutes_total']:,.0f} 分钟\n")
        f.write(f"  平均: {stats['exercise_minutes_avg']:.1f} 分钟/天\n")

        f.write(f"\n站立时间统计:\n")
        f.write(f"  总计: {stats['stand_hours_total']:.1f} 小时\n")
        f.write(f"  平均: {stats['stand_hours_avg']:.1f} 小时/天\n")

        if "weight_avg" in stats:
            f.write(f"\n体重统计:\n")
            f.write(f"  平均: {stats['weight_avg']:.2f} kg\n")
            f.write(f"  范围: {stats['weight_min']:.2f} - {stats['weight_max']:.2f} kg\n")

        if "resting_hr_avg" in stats:
            f.write(f"\n静息心率统计:\n")
            f.write(f"  平均: {stats['resting_hr_avg']:.1f} bpm\n")
            f.write(f"  范围: {stats['resting_hr_min']:.1f} - {stats['resting_hr_max']:.1f} bpm\n")

        if "rolling_metrics_summary" in stats:
            f.write(f"\n滚动指标统计（7日窗口）:\n")
            f.write("-" * 70 + "\n")

            rolling_summary = stats["rolling_metrics_summary"]

            if "weight_7day_avg" in rolling_summary:
                s = rolling_summary["weight_7day_avg"]
                f.write(f"\n体重7日均值: 平均={s['mean']:.2f} kg, 范围={s['min']:.2f}-{s['max']:.2f}\n")

            if "steps_7day_avg" in rolling_summary:
                s = rolling_summary["steps_7day_avg"]
                f.write(f"步数7日均值: 平均={s['mean']:,.0f} 步, 范围={s['min']:,.0f}-{s['max']:,.0f}\n")

            if "exercise_weekly_total" in rolling_summary:
                s = rolling_summary["exercise_weekly_total"]
                f.write(f"每周运动: 平均={s['mean']:.1f} 分钟, 范围={s['min']:.0f}-{s['max']:.0f}\n")

            if "resting_hr_7day_avg" in rolling_summary:
                s = rolling_summary["resting_hr_7day_avg"]
                f.write(f"静息心率7日均值: 平均={s['mean']:.1f} bpm, 范围={s['min']:.1f}-{s['max']:.1f}\n")

            if "hrv_7day_avg" in rolling_summary:
                s = rolling_summary["hrv_7day_avg"]
                f.write(f"HRV 7日均值: 平均={s['mean']:.1f} ms, 范围={s['min']:.1f}-{s['max']:.1f}\n")

            if "low_activity_days_7day" in rolling_summary:
                s = rolling_summary["low_activity_days_7day"]
                f.write(f"低活动日: 平均={s['mean']:.1f} 天, 范围={s['min']}-{s['max']}\n")

    def _export_quality_report(
        self,
        df: pd.DataFrame,
        output_dir: Path
    ) -> Path:
        """导出质量分析报告（简化版）"""
        output_path = output_dir / "quality_analysis_report.txt"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("数据质量分析报告\n")
            f.write("=" * 70 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if "wear_status" not in df.columns:
                f.write("警告: 数据中缺少佩戴状态信息\n")
                return output_path

            total_days = len(df)

            worn_count = sum(df["wear_status"] == "worn")
            not_worn_count = sum(df["wear_status"] == "not_worn")

            f.write(f"总天数: {total_days}\n\n")

            f.write("佩戴状态分布:\n")
            f.write(f"  已佩戴 (worn): {worn_count} ({worn_count/total_days*100:.1f}%)\n")
            f.write(f"  未佩戴 (not_worn): {not_worn_count} ({not_worn_count/total_days*100:.1f}%)\n\n")

            if "is_low_activity_day" in df.columns:
                low_activity_days = sum(df["is_low_activity_day"] == True)
                f.write(f"低活动日 (步数<1000且已佩戴): {low_activity_days} ({low_activity_days/total_days*100:.1f}%)\n")

        logger.info(f"质量报告已导出: {output_path}")

        return output_path
