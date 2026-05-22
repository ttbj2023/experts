#!/usr/bin/env python3
"""完整处理脚本：解析 XML → 质量分析 → 滚动指标 → 周汇总 → 导出 CSV

用法:
    python3 scripts/regenerate_enhanced_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from apple_health_processor.parsers.xml_stream_parser import XMLStreamParser
from apple_health_processor.aggregators import DailyAggregator, WeeklyAggregator, SleepAggregator
from apple_health_processor.exporters import CSVExporter
from apple_health_processor.enhancement.quality_analyzer import QualityAnalyzer
from apple_health_processor.enhancement.rolling_calculator import RollingCalculator
from apple_health_processor.enhancement.sleep_quality_analyzer import SleepQualityAnalyzer


def find_xml():
    candidates = [
        Path("apple_health_export/导出.xml"),
        Path("../apple_health_export/导出.xml"),
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    return None


def main():
    xml_path = find_xml()
    if not xml_path:
        print("未找到 XML 文件，请确认 apple_health_export/导出.xml 存在")
        sys.exit(1)

    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"XML: {xml_path}")
    print(f"输出: {output_dir}")
    print()

    # Step 1: 解析
    print("[1/6] 解析 XML...")
    parser = XMLStreamParser(str(xml_path))
    daily_agg = DailyAggregator()
    sleep_agg = SleepAggregator()
    workouts = []

    for record in parser.iter_records():
        rt = record.get("type", "")
        if "SleepAnalysis" in rt:
            sleep_agg.add_sleep_record(record)
        else:
            daily_agg.add_record(record)

    for summary in parser.iter_activity_summaries():
        daily_agg.add_activity_summary(summary)

    for workout in parser.iter_workouts():
        workouts.append(workout)

    daily_df = daily_agg.get_daily_summary()
    sleep_df = sleep_agg.get_sleep_summary()
    print(f"  daily={len(daily_df)}, sleep={len(sleep_df)}, workout={len(workouts)}")

    # Step 2: 质量分析
    print("[2/6] 质量分析...")
    qa = QualityAnalyzer()
    daily_reset = daily_df.reset_index()
    quality_results = qa.batch_analyze(daily_reset.to_dict("records"))
    for i, q in enumerate(quality_results):
        daily_reset.at[i, "wear_status"] = q["wear_status"]
        daily_reset.at[i, "is_low_activity_day"] = q["is_low_activity_day"]
    daily_df = daily_reset.set_index("date")
    worn = sum(1 for q in quality_results if q["wear_status"] == "worn")
    print(f"  worn={worn}, not_worn={len(quality_results) - worn}")

    # Step 3: 滚动指标
    print("[3/6] 7日滚动指标...")
    rc = RollingCalculator()
    daily_df = rc.calculate_all_rolling_metrics(daily_df)

    # Step 4: 周汇总
    print("[4/6] 周汇总...")
    weekly_df = WeeklyAggregator().aggregate_from_daily(daily_df)
    print(f"  {len(weekly_df)} 周")

    # Step 5: 睡眠增强
    print("[5/6] 睡眠增强...")
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

    # Step 6: 导出
    print("[6/6] 导出 CSV...")
    exporter = CSVExporter(output_dir=str(output_dir))
    results = exporter.export_all(
        daily_df=daily_df,
        weekly_df=weekly_df,
        workouts=workouts,
        sleep_df=sleep_enhanced,
    )

    complete_daily = output_dir / "daily_health_summary_complete.csv"
    export_daily = daily_df.reset_index()
    export_daily["date"] = export_daily["date"].apply(
        lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else str(x)
    )
    export_daily.to_csv(complete_daily, index=False, encoding="utf-8")

    complete_sleep = output_dir / "sleep_summary_complete.csv"
    sleep_enhanced.to_csv(complete_sleep, index=False, encoding="utf-8")

    print()
    for name, path in results.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {path.name} ({size:,} bytes)")
    for p in [complete_daily, complete_sleep]:
        size = p.stat().st_size if p.exists() else 0
        print(f"  {p.name} ({size:,} bytes)")

    print("\n完成!")


if __name__ == "__main__":
    main()
