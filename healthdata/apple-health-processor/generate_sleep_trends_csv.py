#!/usr/bin/env python3
"""睡眠数据处理脚本

将原始睡眠数据处理为以日为单位的CSV，并计算滚动均值、
入睡时间均值等统计指标。

功能：
1. 读取基础睡眠数据
2. 添加时间辅助字段
3. 标记睡眠有效性
4. 计算滚动指标
5. 生成周趋势统计
6. 导出CSV文件
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "src"))

from apple_health_processor.enhancement.sleep_quality_analyzer import SleepQualityAnalyzer
from apple_health_processor.parsers.xml_stream_parser import XMLStreamParser
from apple_health_processor.aggregators.sleep_aggregator import SleepAggregator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def enhance_sleep_time_fields(sleep_df: pd.DataFrame) -> pd.DataFrame:
    """添加时间辅助字段"""
    result_df = sleep_df.copy()

    if 'date' not in result_df.columns and result_df.index.name == 'date':
        result_df = result_df.reset_index()

    if not pd.api.types.is_datetime64_any_dtype(result_df['date']):
        result_df['date'] = pd.to_datetime(result_df['date'])

    result_df['is_weekend'] = result_df['date'].dt.dayofweek >= 5
    result_df['day_of_week'] = result_df['date'].dt.dayofweek

    return result_df


def calculate_circular_time_mean(hours: pd.Series, window: int = 7, min_periods: int = 4) -> pd.Series:
    """计算环形时间的滚动均值

    正确处理跨越午夜的时间平均。
    """
    radians = hours * (2 * np.pi / 24)

    sin_mean = np.sin(radians).rolling(window=window, min_periods=min_periods).mean()
    cos_mean = np.cos(radians).rolling(window=window, min_periods=min_periods).mean()

    mean_hours = np.arctan2(sin_mean, cos_mean) * (24 / (2 * np.pi))
    result = mean_hours % 24

    # 修复浮点精度：24.0 应为 0.0
    result = result.apply(lambda x: 0.0 if isinstance(x, float) and abs(x - 24.0) < 1e-10 else x)

    return result


def calculate_sleep_rolling_metrics(sleep_df: pd.DataFrame) -> pd.DataFrame:
    """计算睡眠滚动指标

    排除无效日（asleep_minutes <= 60），计算7日滚动均值。
    """
    result_df = sleep_df.copy()

    sleep_data_clean = result_df.copy()
    sleep_data_clean.loc[~sleep_data_clean['is_valid_sleep_day'], 'asleep_minutes'] = np.nan
    sleep_data_clean.loc[~sleep_data_clean['is_valid_sleep_day'], 'sleep_efficiency'] = np.nan
    sleep_data_clean.loc[~sleep_data_clean['is_valid_sleep_day'], 'bed_time_hour'] = np.nan
    sleep_data_clean.loc[~sleep_data_clean['is_valid_sleep_day'], 'wake_time_hour'] = np.nan

    result_df['sleep_7day_avg'] = sleep_data_clean['asleep_minutes'].rolling(
        window=7, min_periods=4
    ).mean()

    result_df['sleep_efficiency_7day_avg'] = sleep_data_clean['sleep_efficiency'].rolling(
        window=7, min_periods=4
    ).mean()

    result_df['bed_time_7day_avg_hour'] = calculate_circular_time_mean(
        sleep_data_clean['bed_time_hour'], window=7, min_periods=4
    )

    result_df['wake_time_7day_avg_hour'] = calculate_circular_time_mean(
        sleep_data_clean['wake_time_hour'], window=7, min_periods=4
    )

    return result_df


def generate_weekly_sleep_statistics(sleep_df: pd.DataFrame, weeks_count: int = 8) -> pd.DataFrame:
    """生成周睡眠统计"""
    sleep_df_copy = sleep_df.copy()
    sleep_df_copy['year'] = sleep_df_copy['date'].dt.year
    sleep_df_copy['week'] = sleep_df_copy['date'].dt.isocalendar().week

    end_date = sleep_df_copy['date'].max()
    start_date = end_date - pd.DateOffset(weeks=weeks_count)
    recent_df = sleep_df_copy[sleep_df_copy['date'] >= start_date].copy()

    if recent_df.empty:
        logger.warning(f"最近{weeks_count}周没有睡眠数据")
        return pd.DataFrame()

    agg_dict = {
        'date': ['min', 'max', 'count'],
        'in_bed_minutes': ['sum', 'mean', 'min', 'max'],
        'asleep_minutes': ['sum', 'mean', 'min', 'max'],
        'sleep_efficiency': ['mean', 'min', 'max'],
        'bed_time_hour': 'mean',
        'wake_time_hour': 'mean',
    }

    if 'deep_sleep_minutes' in recent_df.columns:
        agg_dict['deep_sleep_minutes'] = ['mean', 'sum']

    weekly_raw = recent_df.groupby(['year', 'week']).agg(agg_dict)

    columns = [
        'week_start', 'week_end', 'days_count',
        'raw_in_bed_total', 'raw_in_bed_avg', 'raw_in_bed_min', 'raw_in_bed_max',
        'raw_asleep_total', 'raw_asleep_avg', 'raw_asleep_min', 'raw_asleep_max',
        'raw_sleep_efficiency_avg', 'raw_sleep_efficiency_min', 'raw_sleep_efficiency_max',
        'raw_bed_time_avg_hour', 'raw_wake_time_avg_hour',
    ]
    if 'deep_sleep_minutes' in recent_df.columns:
        columns.extend(['raw_deep_sleep_avg', 'raw_deep_sleep_total'])

    weekly_raw.columns = columns

    valid_df = recent_df[recent_df['is_valid_sleep_day']].copy()
    if not valid_df.empty:
        weekly_valid = valid_df.groupby(['year', 'week']).agg({
            'asleep_minutes': ['mean', 'count'],
            'sleep_efficiency': 'mean',
            'bed_time_hour': 'mean',
        })
        weekly_valid.columns = [
            'valid_asleep_avg', 'valid_days_count',
            'valid_sleep_efficiency_avg', 'valid_bed_time_avg_hour'
        ]
    else:
        weekly_valid = pd.DataFrame(columns=[
            'valid_asleep_avg', 'valid_days_count',
            'valid_sleep_efficiency_avg', 'valid_bed_time_avg_hour'
        ])
        weekly_valid.index.names = ['year', 'week']

    weekly_summary = weekly_raw.reset_index()
    weekly_summary = weekly_summary.merge(weekly_valid.reset_index(), on=['year', 'week'], how='left')

    weekly_summary['is_full_week'] = weekly_summary['days_count'] >= 7
    weekly_summary['completeness_ratio'] = (weekly_summary['days_count'] / 7).round(2)

    weekly_summary['week_label'] = (
        weekly_summary['year'].astype(str) + '-W' +
        weekly_summary['week'].astype(str).str.zfill(2)
    )

    numeric_cols = [
        'valid_days_count', 'valid_asleep_avg', 'valid_sleep_efficiency_avg', 'valid_bed_time_avg_hour',
    ]
    for col in numeric_cols:
        if col in weekly_summary.columns:
            if 'count' in col:
                weekly_summary[col] = weekly_summary[col].fillna(0).astype(int)
            else:
                weekly_summary[col] = weekly_summary[col].fillna(0)

    return weekly_summary


def export_sleep_data(daily_df: pd.DataFrame, weekly_df: pd.DataFrame, output_dir: Path) -> tuple:
    """导出睡眠数据CSV"""
    output_dir.mkdir(parents=True, exist_ok=True)

    daily_file = output_dir / "sleep_daily_enhanced.csv"
    daily_df.to_csv(daily_file, index=False, encoding='utf-8')
    logger.info(f"日级睡眠数据已导出: {daily_file}")

    weekly_file = output_dir / "sleep_weekly_trends.csv"
    weekly_df.to_csv(weekly_file, index=False, encoding='utf-8')
    logger.info(f"周趋势睡眠数据已导出: {weekly_file}")

    return daily_file, weekly_file


def generate_sleep_trends_from_xml(xml_file: Path, output_dir: Path = None) -> tuple:
    """从XML文件生成睡眠趋势分析"""
    if output_dir is None:
        output_dir = Path("output/sleep_analysis")

    logger.info(f"开始处理睡眠数据: {xml_file}")

    logger.info("步骤1: 解析XML并聚合睡眠数据")
    parser = XMLStreamParser(xml_file)
    sleep_aggregator = SleepAggregator()

    for record in parser.iter_records():
        sleep_aggregator.add_sleep_record(record)

    sleep_df = sleep_aggregator.get_sleep_summary()

    if sleep_df.empty:
        logger.error("没有找到有效的睡眠数据")
        return pd.DataFrame(), pd.DataFrame()

    sleep_df.reset_index(inplace=True)
    logger.info(f"解析完成，共{len(sleep_df)}天的睡眠数据")

    logger.info("步骤2: 添加时间辅助字段")
    sleep_df = enhance_sleep_time_fields(sleep_df)

    logger.info("步骤3: 标记睡眠有效性")
    quality_analyzer = SleepQualityAnalyzer()
    sleep_df = quality_analyzer.batch_analyze(sleep_df)

    valid_count = sleep_df['is_valid_sleep_day'].sum()
    logger.info(f"有效性标记完成: {valid_count}/{len(sleep_df)} 天有效")

    logger.info("步骤4: 计算7日滚动指标")
    sleep_df = calculate_sleep_rolling_metrics(sleep_df)

    logger.info("步骤5: 生成周趋势统计（最近8周）")
    weekly_sleep = generate_weekly_sleep_statistics(sleep_df, weeks_count=8)

    logger.info("步骤6: 导出CSV文件")
    export_sleep_data(sleep_df, weekly_sleep, output_dir)

    logger.info("睡眠趋势分析完成!")
    return sleep_df, weekly_sleep


def generate_sleep_trends_from_csv(input_csv: Path, output_dir: Path = None) -> tuple:
    """从现有CSV文件生成睡眠趋势分析"""
    if output_dir is None:
        output_dir = Path("output/sleep_analysis")

    logger.info(f"开始处理睡眠数据CSV: {input_csv}")

    sleep_df = pd.read_csv(input_csv)
    sleep_df['date'] = pd.to_datetime(sleep_df['date'])

    if 'bed_time' in sleep_df.columns and not pd.api.types.is_datetime64_any_dtype(sleep_df['bed_time']):
        sleep_df['bed_time'] = pd.to_datetime(sleep_df['bed_time'])

    if 'wake_time' in sleep_df.columns and not pd.api.types.is_datetime64_any_dtype(sleep_df['wake_time']):
        sleep_df['wake_time'] = pd.to_datetime(sleep_df['wake_time'])

    logger.info(f"读取完成，共{len(sleep_df)}天的睡眠数据")

    logger.info("步骤1: 添加时间辅助字段")
    sleep_df = enhance_sleep_time_fields(sleep_df)

    logger.info("步骤2: 标记睡眠有效性")
    quality_analyzer = SleepQualityAnalyzer()
    sleep_df = quality_analyzer.batch_analyze(sleep_df)

    valid_count = sleep_df['is_valid_sleep_day'].sum()
    logger.info(f"有效性标记完成: {valid_count}/{len(sleep_df)} 天有效")

    logger.info("步骤3: 计算7日滚动指标")
    sleep_df = calculate_sleep_rolling_metrics(sleep_df)

    logger.info("步骤4: 生成周趋势统计（最近8周）")
    weekly_sleep = generate_weekly_sleep_statistics(sleep_df, weeks_count=8)

    logger.info("步骤5: 导出CSV文件")
    export_sleep_data(sleep_df, weekly_sleep, output_dir)

    logger.info("睡眠趋势分析完成!")
    return sleep_df, weekly_sleep


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='生成睡眠趋势分析CSV')
    parser.add_argument('--input', type=str, help='输入文件路径（XML或CSV）')
    parser.add_argument('--output-dir', type=str, default='output/sleep_analysis', help='输出目录路径')

    args = parser.parse_args()

    if args.input:
        input_file = Path(args.input)
        if not input_file.exists():
            logger.error(f"输入文件不存在: {input_file}")
            sys.exit(1)
    else:
        output_base = Path("output")
        possible_files = [
            output_base / "sleep_summary.csv",
            output_base / "daily_health_summary.csv",
        ]

        input_file = None
        for file in possible_files:
            if file.exists():
                input_file = file
                break

        if not input_file:
            logger.error("找不到输入文件，请使用--input参数指定")
            sys.exit(1)

    output_dir = Path(args.output_dir)

    if input_file.suffix.lower() == '.xml':
        daily_df, weekly_df = generate_sleep_trends_from_xml(input_file, output_dir)
    elif input_file.suffix.lower() == '.csv':
        daily_df, weekly_df = generate_sleep_trends_from_csv(input_file, output_dir)
    else:
        logger.error(f"不支持的文件类型: {input_file.suffix}")
        sys.exit(1)

    if not daily_df.empty and not weekly_df.empty:
        print("\n" + "=" * 60)
        print("睡眠趋势分析完成")
        print("=" * 60)
        print(f"\n日级数据: {len(daily_df)}天")
        print(f"周趋势数据: {len(weekly_df)}周")
        print(f"\n输出目录: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
