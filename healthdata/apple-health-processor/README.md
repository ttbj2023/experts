# Apple Health 数据处理器

处理 Apple Health 导出的 XML 数据，生成健康分析所需的 CSV 汇总表。

## 功能特性

- **流式 XML 解析**: 使用 `lxml.etree.iterparse` 增量解析，支持 686MB+ 大文件
- **跨天记录拆分**: 累加类型（步数/能量/距离）按时间比例拆分到对应日期
- **睡眠去重**: 自动合并同一时间段的重复记录（Sleepace 等设备）
- **深度睡眠追踪**: 独立统计 Deep Sleep 时长
- **佩戴状态检测**: 基于 stand_hours / active_energy 判定设备佩戴
- **7 日滚动指标**: 体重、步数、心率、HRV、运动时长、低活动天数
- **运动心率**: 从 WorkoutStatistics 子元素提取平均/最大心率
- **晨起值选择**: 体重/体脂/肌肉量优先取 6-10 点测量值

## 安装

```bash
uv sync
```

## 使用方法

### 完整处理（推荐）

```bash
# 生成包含所有增强指标的完整 CSV
python3 scripts/regenerate_enhanced_data.py
```

### 睡眠专项分析

```bash
python3 generate_sleep_trends_csv.py --input apple_health_export/导出.xml --output-dir output/sleep_analysis
```

### 基础处理（仅原始聚合）

```bash
.venv/bin/python -m apple_health_processor.cli apple_health_export/导出.xml -o output
```

## 输出文件

`output/` 目录下生成以下文件：

| 文件 | 说明 |
|------|------|
| `daily_health_summary_complete.csv` | 完整版每日数据（含佩戴状态 + 7日滚动指标） |
| `weekly_health_summary.csv` | 每周汇总（仅统计佩戴天，<4天不计算日均值） |
| `sleep_summary_complete.csv` | 睡眠数据（含深度睡眠 + 有效性标记 + 7日滚动均值） |
| `workout_records.csv` | 运动记录（含平均/最大心率） |
| `daily_health_summary.csv` | 基础版每日数据（不含增强指标） |
| `sleep_summary.csv` | 基础版睡眠数据（不含滚动均值） |

## 数据字段说明

### 每日数据 (daily)

| 字段 | 单位 | 来源 | 说明 |
|------|------|------|------|
| `steps` | 步 | 原始累加 | 日步数（跨天记录按比例拆分） |
| `active_energy_kcal` | kcal | 原始累加 | 活动能量 |
| `basal_energy_kcal` | kcal | 原始累加 | 基础代谢（跨天记录按比例拆分） |
| `distance_km` | km | 原始累加 | 步行+跑步距离 |
| `exercise_minutes` | 分钟 | 优先 ActivitySummary | 运动时长 |
| `stand_hours` | 小时 | ActivitySummary | 站立小时数 |
| `body_mass_kg` | kg | 晨起值 | 6-10点首个测量值 |
| `body_fat_pct` | % | 晨起值 | XML 小数形式 ×100 转百分比 |
| `muscle_mass_kg` | kg | 晨起值 | 去脂体重 |
| `resting_hr_bpm` | bpm | 日均值 | 静息心率 |
| `hrv_ms` | ms | 日均值 | 心率变异性 SDNN |
| `vo2_max` | ml/kg/min | 日均值 | 最大摄氧量 |
| `wear_status` | - | 算法判定 | `worn` / `not_worn`（基于 stand>0 或 active_energy>0） |
| `is_low_activity_day` | - | 算法判定 | steps<1000 且已佩戴 |
| `weight_7day_avg` | kg | 7日滚动 | 排除异常值和未佩戴天 |
| `steps_7day_avg` | 步 | 7日滚动 | 排除未佩戴天 |
| `resting_hr_7day_avg` | bpm | 7日滚动 | 排除未佩戴天 |
| `hrv_7day_avg` | ms | 7日滚动 | 排除未佩戴天 |
| `exercise_weekly_total` | 分钟 | 7日滚动 | 排除未佩戴天 |
| `low_activity_days_7day` | 天 | 7日滚动 | 窗口内低活动天数 |

### 睡眠数据 (sleep)

| 字段 | 单位 | 说明 |
|------|------|------|
| `bed_time` | datetime | 入床时间 |
| `wake_time` | datetime | 起床时间（按此日期归属） |
| `in_bed_minutes` | 分钟 | 在床总时长 |
| `asleep_minutes` | 分钟 | 入睡总时长（含深度） |
| `deep_sleep_minutes` | 分钟 | 深度睡眠时长 |
| `awake_minutes` | 分钟 | 睡眠中清醒时长 |
| `sleep_efficiency` | % | asleep / in_bed × 100 |
| `is_valid_sleep_day` | bool | asleep_minutes > 60 |
| `sleep_7day_avg` | 分钟 | 7日滚动均值（排除无效天） |

### 运动数据 (workout)

| 字段 | 单位 | 说明 |
|------|------|------|
| `workout_type` | - | 运动类型 |
| `duration_minutes` | 分钟 | 持续时间 |
| `distance_km` | km | 距离 |
| `energy_kcal` | kcal | 消耗卡路里 |
| `heart_rate_avg` | bpm | 平均心率（从 WorkoutStatistics 提取） |
| `heart_rate_max` | bpm | 最大心率（从 WorkoutStatistics 提取） |

## 核心算法

### 跨天记录拆分

累加类型（steps/active_energy/basal_energy/distance）的记录若 startDate 和 endDate 不在同一天，按每天实际覆盖的秒数比例分配 value。例如一条 24 小时的 basal 记录会被精确拆分到两个日期。

### 睡眠去重

按 `(start, end, sleep_state)` 三元组去重，消除 Sleepace 等设备在同一时间段重复上报的数据。同时过滤 duration ≤ 0 的无效记录。

### 周汇总

仅统计 `wear_status == "worn"` 的天数。有效天数 < 4 的周不计算日均值（设为空），累加总值仍保留。

## 项目结构

```
apple-health-processor/
├── config/
│   └── health_data_config.yaml         # 数据类型映射和输出配置
├── docs/
│   ├── ASSISTANT_HEALTH_DB_SCHEMA.md   # 目标数据库字段参考
│   └── DB_SCHEMA_CHANGES.md            # 数据库适配变更说明
├── scripts/
│   └── regenerate_enhanced_data.py      # 完整处理脚本
├── src/apple_health_processor/
│   ├── cli.py                           # 命令行入口
│   ├── parsers/
│   │   └── xml_stream_parser.py         # XML 流式解析器
│   ├── aggregators/
│   │   ├── daily_aggregator.py          # 每日聚合（含跨天拆分）
│   │   ├── weekly_aggregator.py         # 每周聚合（仅佩戴天）
│   │   └── sleep_aggregator.py          # 睡眠聚合（含去重+深度睡眠）
│   ├── enhancement/
│   │   ├── quality_analyzer.py          # 佩戴/低活动判定
│   │   ├── rolling_calculator.py        # 7日滚动指标
│   │   ├── sleep_quality_analyzer.py    # 睡眠有效性标记
│   │   └── enhanced_exporter.py         # 报告导出
│   └── exporters/
│       └── csv_exporter.py              # CSV 导出器
├── tests/
│   ├── test_processor.py                # 基础流程测试
│   └── fixtures/sample_data.xml         # 测试数据
├── generate_sleep_trends_csv.py         # 睡眠专项分析脚本
├── pyproject.toml
└── output/                              # 输出目录
```

## 性能

- 处理速度：约 150 万条记录 / 2 分钟
- 内存占用：恒定，不随 XML 文件大小增长
