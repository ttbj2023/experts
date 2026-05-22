"""命令行界面 (CLI)

Apple Health 数据处理器的命令行入口。
"""

import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import click
import yaml
from tqdm import tqdm

from .parsers import XMLStreamParser
from .aggregators import DailyAggregator, WeeklyAggregator, SleepAggregator
from .exporters import CSVExporter
from .enhancement.quality_analyzer import QualityAnalyzer
from .enhancement.rolling_calculator import RollingCalculator
from .enhancement.sleep_quality_analyzer import SleepQualityAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("xml_file", type=click.Path(exists=True))
@click.option("-o", "--output", default="output", show_default=True, help="输出目录路径")
@click.option("-t", "--test-mode", is_flag=True, help="测试模式：只处理最近 14 天")
@click.option("-v", "--verbose", is_flag=True, help="详细输出模式")
@click.option("--days", type=int, default=14, show_default=True, help="测试模式下处理的天数")
def cli(xml_file: str, output: str, test_mode: bool, verbose: bool, days: int):
    """Apple Health 数据处理器

    处理 Apple Health 导出的 XML 数据，生成完整 CSV 汇总表。

    示例:

        python -m apple_health_processor.cli apple_health_export/导出.xml

        python -m apple_health_processor.cli apple_health_export/导出.xml -o output
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Apple Health 数据处理器启动")
    logger.info(f"输入: {xml_file}")
    logger.info(f"输出: {output}")

    date_filter = None
    if test_mode:
        date_filter = datetime.now(timezone.utc) - timedelta(days=days)
        logger.info(f"测试模式: 只处理 {date_filter.date()} 之后的数据")

    # 解析 XML
    parser = XMLStreamParser(xml_file)
    daily_agg = DailyAggregator()
    sleep_agg = SleepAggregator()
    workouts = []

    logger.info("处理健康记录...")
    record_count = 0
    with tqdm(desc="记录", unit="条") as pbar:
        for record in parser.iter_records():
            if date_filter:
                sd = record.get("startDate")
                if sd and isinstance(sd, datetime) and sd < date_filter:
                    continue

            rt = record.get("type", "")
            if "SleepAnalysis" in rt:
                sleep_agg.add_sleep_record(record)
            else:
                daily_agg.add_record(record)
            record_count += 1
            pbar.update(1)

    logger.info(f"处理 {record_count} 条记录")

    for summary in parser.iter_activity_summaries():
        if date_filter:
            sd = summary.get("date")
            if sd and isinstance(sd, datetime) and sd < date_filter:
                continue
        daily_agg.add_activity_summary(summary)

    for workout in parser.iter_workouts():
        if date_filter:
            sd = workout.get("startDate")
            if sd and isinstance(sd, datetime) and sd < date_filter:
                continue
        workouts.append(workout)

    # 质量分析
    logger.info("质量分析...")
    qa = QualityAnalyzer()
    daily_df = daily_agg.get_daily_summary()
    daily_reset = daily_df.reset_index()
    quality_results = qa.batch_analyze(daily_reset.to_dict("records"))
    for i, q in enumerate(quality_results):
        daily_reset.at[i, "wear_status"] = q["wear_status"]
        daily_reset.at[i, "is_low_activity_day"] = q["is_low_activity_day"]
    daily_df = daily_reset.set_index("date")

    # 滚动指标
    logger.info("计算7日滚动指标...")
    rc = RollingCalculator()
    daily_df = rc.calculate_all_rolling_metrics(daily_df)

    # 周汇总
    logger.info("生成周汇总...")
    weekly_df = WeeklyAggregator().aggregate_from_daily(daily_df)

    # 睡眠
    logger.info("生成睡眠汇总...")
    import numpy as np

    sleep_df = sleep_agg.get_sleep_summary()
    sleep_reset = sleep_df.reset_index()
    sqa = SleepQualityAnalyzer()
    sleep_enhanced = sqa.batch_analyze(sleep_reset)

    sleep_clean = sleep_enhanced.copy()
    sleep_clean.loc[~sleep_clean["is_valid_sleep_day"], "asleep_minutes"] = np.nan
    sleep_clean.loc[~sleep_clean["is_valid_sleep_day"], "sleep_efficiency"] = np.nan
    if "bed_time_hour" in sleep_clean.columns:
        sleep_clean.loc[~sleep_clean["is_valid_sleep_day"], "bed_time_hour"] = np.nan
        sleep_clean.loc[~sleep_clean["is_valid_sleep_day"], "wake_time_hour"] = np.nan
    sleep_enhanced["sleep_7day_avg"] = sleep_clean["asleep_minutes"].rolling(window=7, min_periods=4).mean()
    sleep_enhanced["sleep_efficiency_7day_avg"] = sleep_clean["sleep_efficiency"].rolling(window=7, min_periods=4).mean()

    # 导出
    logger.info("导出 CSV...")
    exporter = CSVExporter(output_dir=output)
    results = exporter.export_all(
        daily_df=daily_df,
        weekly_df=weekly_df,
        workouts=workouts,
        sleep_df=sleep_enhanced,
    )

    complete_daily = Path(output) / "daily_health_summary_complete.csv"
    export_daily = daily_df.reset_index()
    export_daily["date"] = export_daily["date"].apply(
        lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else str(x)
    )
    export_daily.to_csv(complete_daily, index=False, encoding="utf-8")

    complete_sleep = Path(output) / "sleep_summary_complete.csv"
    sleep_enhanced.to_csv(complete_sleep, index=False, encoding="utf-8")

    logger.info("=" * 60)
    logger.info("处理完成")
    logger.info("=" * 60)
    for name, path in results.items():
        size = path.stat().st_size if path.exists() else 0
        logger.info(f"  {path.name} ({size:,} bytes)")
    for p in [complete_daily, complete_sleep]:
        size = p.stat().st_size if p.exists() else 0
        logger.info(f"  {p.name} ({size:,} bytes)")


if __name__ == "__main__":
    cli()
