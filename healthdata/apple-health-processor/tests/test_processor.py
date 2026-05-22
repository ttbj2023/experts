"""测试脚本

验证 Apple Health 数据处理器的基本功能。
"""

import sys
from pathlib import Path

# 添加 src 到 Python 路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from apple_health_processor.parsers import XMLStreamParser
from apple_health_processor.aggregators import DailyAggregator, WeeklyAggregator, SleepAggregator
from apple_health_processor.exporters import CSVExporter


def test_processor():
    """测试处理器基本功能"""
    print("=" * 60)
    print("Apple Health 数据处理器测试")
    print("=" * 60)

    # 测试数据路径
    test_xml = Path(__file__).parent / "fixtures" / "sample_data.xml"
    output_dir = Path(__file__).parent.parent / "output_test"

    print(f"\n输入文件: {test_xml}")
    print(f"输出目录: {output_dir}")

    # 初始化解析器
    print("\n[1/6] 初始化 XML 流式解析器...")
    parser = XMLStreamParser(str(test_xml))

    # 初始化聚合器
    print("[2/6] 初始化聚合器...")
    daily_aggregator = DailyAggregator()
    weekly_aggregator = WeeklyAggregator()
    sleep_aggregator = SleepAggregator()

    workout_records = []

    # 处理健康数据记录
    print("[3/6] 处理健康数据记录...")
    record_count = 0
    for record in parser.iter_records():
        record_type = record.get("type", "")

        # 睡眠记录
        if "SleepAnalysis" in record_type:
            sleep_aggregator.add_sleep_record(record)
        # 其他健康记录
        else:
            daily_aggregator.add_record(record)

        record_count += 1

    print(f"  ✓ 处理了 {record_count} 条健康记录")

    # 处理活动汇总数据
    print("[4/6] 处理活动汇总数据...")
    activity_count = 0
    for summary in parser.iter_activity_summaries():
        daily_aggregator.add_activity_summary(summary)
        activity_count += 1

    print(f"  ✓ 处理了 {activity_count} 条活动汇总")

    # 处理运动记录
    print("[5/6] 处理运动记录...")
    workout_count = 0
    for workout in parser.iter_workouts():
        workout_records.append(workout)
        workout_count += 1

    print(f"  ✓ 处理了 {workout_count} 条运动记录")

    # 生成汇总数据
    print("\n[6/6] 生成汇总数据...")
    daily_df = daily_aggregator.get_daily_summary()
    print(f"  ✓ 每日汇总: {len(daily_df)} 天")

    weekly_df = weekly_aggregator.aggregate_from_daily(daily_df)
    print(f"  ✓ 每周汇总: {len(weekly_df)} 周")

    sleep_df = sleep_aggregator.get_sleep_summary()
    print(f"  ✓ 睡眠汇总: {len(sleep_df)} 晚")

    # 显示部分数据
    print("\n" + "=" * 60)
    print("每日数据预览")
    print("=" * 60)
    if not daily_df.empty:
        display_cols = [
            "steps", "body_mass_kg", "body_fat_pct", "muscle_mass_kg",
            "resting_hr_bpm", "hrv_ms", "vo2_max",
        ]
        existing_cols = [c for c in display_cols if c in daily_df.columns]
        print(daily_df[existing_cols].head().to_string())

    print("\n" + "=" * 60)
    print("运动记录预览")
    print("=" * 60)
    for workout in workout_records:
        hr_avg = workout.get("heart_rate_avg")
        hr_max = workout.get("heart_rate_max")
        hr_info = f", 心率: avg={hr_avg}, max={hr_max}" if hr_avg else ""
        print(f"  {workout.get('type')}: {workout.get('duration_seconds') / 60:.1f} 分钟{hr_info}")

    print("\n" + "=" * 60)
    print("睡眠数据预览")
    print("=" * 60)
    if not sleep_df.empty:
        print(sleep_df.head().to_string())

    # 导出 CSV 文件
    print(f"\n导出 CSV 文件到: {output_dir}")
    exporter = CSVExporter(output_dir=str(output_dir))
    results = exporter.export_all(
        daily_df=daily_df,
        weekly_df=weekly_df,
        workouts=workout_records,
        sleep_df=sleep_df,
    )

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    print(f"输出目录: {output_dir}")
    for name, path in results.items():
        file_size = path.stat().st_size if path.exists() else 0
        print(f"  ✓ {name}: {path.name} ({file_size:,} bytes)")


if __name__ == "__main__":
    test_processor()
