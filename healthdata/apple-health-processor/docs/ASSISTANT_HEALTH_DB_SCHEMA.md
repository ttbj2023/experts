# Assistant 健康数据库字段参考

本文档记录 Assistant 项目健康数据库 (`health_data.db`) 的完整表结构和字段定义, 供 apple-health-processor 输出数据时参考字段名和单位.

> 数据库模型源文件: `assistant/src/storage/models/health_data.py`

## 概述

- **数据库类型**: SQLite, 每个 user_id + thread_id 拥有独立的 `health_data.db`
- **表数量**: 8 张表 (另有 1 张已弃用)
- **数据来源**: `data_source` 字段区分 `"manual"` (对话提取) 和 `"apple_health"` (CSV导入)
- **冲突策略**: 导入时仅填充空字段, 已有数据不覆盖

---

## 表 1: daily_health_summary (每日健康汇总)

核心宽表, 每日一行, 唯一约束 `record_date`.

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `record_date` | date | - | 记录日期 (YYYY-MM-DD), **唯一约束** |
| **活动指标** | | | |
| `steps` | int | 步 | 步数 |
| `active_energy_kcal` | float | kcal | 活动能量消耗 |
| `basal_energy_kcal` | float | kcal | 基础代谢能量消耗 |
| `distance_km` | float | km | 步行+跑步距离 |
| `exercise_minutes` | float | 分钟 | 运动时长 |
| `stand_hours` | int | 小时 | 站立小时数 |
| **身体指标** | | | |
| `body_mass_kg` | float | kg | 体重 |
| `body_fat_pct` | float | % | 体脂率 |
| `muscle_mass_kg` | float | kg | 肌肉量 |
| `resting_hr_bpm` | float | bpm | 静息心率 |
| `hrv_ms` | float | ms | 心率变异性 SDNN |
| `vo2_max` | float | ml/kg/min | 最大摄氧量 |
| **睡眠指标** | | | |
| `bed_time` | datetime | - | 入床时间 (含时区, 如 `2026-05-21T03:54:00+08:00`) |
| `wake_time` | datetime | - | 起床时间 (含时区) |
| `in_bed_minutes` | int | 分钟 | 在床时长 |
| `asleep_minutes` | int | 分钟 | 实际入睡时长 |
| `deep_sleep_minutes` | float | 分钟 | 深度睡眠时长 (Apple Watch数据, 可能为空) |
| `awake_minutes` | int | 分钟 | 睡眠中清醒时长 |
| `sleep_efficiency` | float | % | 睡眠效率 (asleep/in_bed * 100) |
| `sleep_duration_hours` | float | 小时 | 睡眠时长 |
| **数据质量** | | | |
| `wear_status` | str | - | 佩戴状态: `worn` / `not_worn` |
| `is_low_activity_day` | bool | - | 是否低活动日 (steps<1000 且 worn) |
| **7日滚动指标** | | | |
| `weight_7d_avg` | float | kg | 7日体重均值 |
| `steps_7d_avg` | float | 步 | 7日步数均值 |
| `resting_hr_7d_avg` | float | bpm | 7日静息心率均值 |
| `hrv_7d_avg` | float | ms | 7日HRV均值 |
| `exercise_7d_total` | float | 分钟 | 7日运动总时长 |
| `sleep_7d_avg` | float | 分钟 | 7日睡眠均值 |
| `sleep_efficiency_7d_avg` | float | % | 7日睡眠效率均值 |
| **元数据** | | | |
| `data_source` | str | - | 数据来源: `manual` / `apple_health` |
| `created_at` | datetime | - | 创建时间 (自动) |
| `updated_at` | datetime | - | 最后更新时间 (自动) |

---

## 表 2: weekly_health_summary (每周健康趋势)

预计算的周维度汇总, 以周一为起始日, 唯一约束 `week_start`.

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `week_start` | date | - | 周一日期 (YYYY-MM-DD), **唯一约束** |
| **活动指标** | | | |
| `steps_total` | float | 步 | 周总步数 |
| `steps_daily_avg` | float | 步 | 周日均步数 |
| `active_energy_total` | float | kcal | 周总活动能量 |
| `active_energy_daily_avg` | float | kcal | 周日均活动能量 |
| `basal_energy_total` | float | kcal | 周总基础代谢能量 |
| `distance_total` | float | km | 周总距离 |
| `distance_daily_avg` | float | km | 周日均距离 |
| `exercise_minutes_total` | float | 分钟 | 周总运动时长 |
| `stand_hours_total` | float | 小时 | 周总站立小时数 |
| **身体指标** | | | |
| `body_mass_avg` | float | kg | 周均体重 |
| `resting_hr_avg` | float | bpm | 周均静息心率 |
| `hrv_avg` | float | ms | 周均HRV |
| `vo2_max_avg` | float | ml/kg/min | 周均VO2Max |
| **睡眠指标** | | | |
| `sleep_duration_avg` | float | 小时 | 周均睡眠时长 |
| `sleep_efficiency_avg` | float | % | 周均睡眠效率 |
| **数据覆盖** | | | |
| `valid_days` | int | 天 | 有效数据天数 |
| `total_days` | int | 天 | 总天数 (通常为7) |
| **元数据** | | | |
| `created_at` | datetime | - | 创建时间 (自动) |
| `updated_at` | datetime | - | 最后更新时间 (自动) |

---

## 表 3: workout_records (运动记录)

每次运动一条记录.

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `workout_type` | str | - | 运动类型: Running/Cycling/Swimming/Hiking等 |
| `duration` | float | **分钟** | 持续时间 |
| `distance` | float? | **km** | 距离 (可选) |
| `calories` | float? | kcal | 消耗卡路里 (可选) |
| `heart_rate_avg` | float? | bpm | 平均心率 (可选) |
| `heart_rate_max` | float? | bpm | 最大心率 (可选) |
| `start_time` | datetime | - | 开始时间 (含时区) |
| `source` | str | - | 数据来源: `manual` / `apple_health` |
| `created_at` | datetime | - | 创建时间 (自动) |

> **注意**: `duration` 单位为**分钟** (非秒), `distance` 单位为**km** (非米).

---

## 表 4: meal_records (饮食记录)

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `meal_type` | str | - | 餐型: `breakfast` / `lunch` / `dinner` / `snack` |
| `meal_date` | date | - | 用餐日期 |
| `items` | JSON | - | 摄入项列表, 每项含 name/calories/protein/carbs/fat |
| `total_calories` | float? | kcal | 总卡路里 |
| `total_protein` | float? | g | 总蛋白质 |
| `total_carbs` | float? | g | 总碳水化合物 |
| `total_fat` | float? | g | 总脂肪 |
| `notes` | str? | - | 备注 |
| `created_at` | datetime | - | 创建时间 (自动) |

---

## 表 5: user_profiles (用户资料)

每个数据库最多一条记录.

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `age` | int? | 岁 | 年龄 |
| `gender` | str? | - | 性别: `male` / `female` / `other` |
| `height` | float? | cm | 身高 |
| `activity_level` | str? | - | 活动水平: `sedentary` / `light` / `moderate` / `active` |
| `created_at` | datetime | - | 创建时间 (自动) |
| `updated_at` | datetime | - | 最后更新时间 (自动) |

---

## 表 6: health_goals (健康目标)

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `goal_type` | str | - | 目标类型: `weight_loss` / `muscle_gain` / `blood_sugar_control` |
| `target_value` | float | - | 目标值 |
| `current_value` | float | - | 当前值 |
| `start_date` | datetime | - | 开始日期 |
| `target_date` | datetime | - | 目标日期 |
| `status` | str | - | 状态: `active` / `completed` / `paused` |
| `created_at` | datetime | - | 创建时间 (自动) |
| `updated_at` | datetime | - | 最后更新时间 (自动) |

---

## 表 7: medical_reports (体检报告)

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `report_date` | datetime | - | 报告日期 |
| `report_data` | JSON | - | 报告数据 (扁平键值对, 如 `{"blood_pressure": "120/80"}`) |
| `report_type` | str? | - | 报告类型: `routine` / `specialized` |
| `created_at` | datetime | - | 创建时间 (自动) |

---

## 表 8: shopping_items (购物清单)

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `id` | int | - | 主键 |
| `product_id` | str | - | 商品ID |
| `name` | str | - | 商品名称 |
| `brand` | str? | - | 品牌 |
| `quantity` | int | - | 数量 |
| `unit` | str | - | 单位 (如 袋/盒) |
| `weight_per_unit` | float | g | 单位重量 |
| `ingredients` | str? | - | 成分列表 |
| `nutrition_per_100g` | JSON | - | 每100g营养成分 (calories/protein/carbs/fat/fiber/sugar/sodium等) |
| `allergens` | JSON? | - | 过敏原列表 (字符串数组) |
| `purchase_date` | datetime | - | 购买日期 |
| `created_at` | datetime | - | 创建时间 (自动) |

---

## CSV 导入字段映射

### daily_health_summary CSV → DB 字段映射

| CSV 列名 | DB 字段 | 转换 |
|----------|---------|------|
| `date` | `record_date` | str → date |
| `steps` | `steps` | float → int |
| `active_energy_kcal` | `active_energy_kcal` | 直接 |
| `basal_energy_kcal` | `basal_energy_kcal` | 直接 |
| `distance_km` | `distance_km` | 直接 |
| `exercise_minutes` | `exercise_minutes` | 直接 |
| `stand_hours` | `stand_hours` | float → int |
| `body_mass_kg` | `body_mass_kg` | 直接 |
| `resting_hr_bpm` | `resting_hr_bpm` | 直接 |
| `hrv_ms` | `hrv_ms` | 直接 |
| `vo2_max` | `vo2_max` | 直接 |
| `wear_status` | `wear_status` | 直接 |
| `is_low_activity_day` | `is_low_activity_day` | 直接 |
| `weight_7day_avg` | `weight_7d_avg` | 直接 |
| `steps_7day_avg` | `steps_7d_avg` | 直接 |
| `resting_hr_7day_avg` | `resting_hr_7d_avg` | 直接 |
| `hrv_7day_avg` | `hrv_7d_avg` | 直接 |
| `exercise_weekly_total` | `exercise_7d_total` | 直接 |

### sleep CSV → daily_health_summary 睡眠字段映射

睡眠数据按 `date` 合并到已有的 daily 记录.

| CSV 列名 | DB 字段 | 转换 |
|----------|---------|------|
| `date` | *(匹配键)* | 用于定位 record_date |
| `bed_time` | `bed_time` | str → datetime |
| `wake_time` | `wake_time` | str → datetime |
| `in_bed_minutes` | `in_bed_minutes` | 直接 |
| `asleep_minutes` | `asleep_minutes` | 直接 |
| `deep_sleep_minutes` | `deep_sleep_minutes` | 直接 |
| `awake_minutes` | `awake_minutes` | 直接 |
| `sleep_efficiency` | `sleep_efficiency` | 直接 |
| `sleep_duration_hours` | `sleep_duration_hours` | 直接 |
| `sleep_7day_avg` | `sleep_7d_avg` | 直接 (分钟) |
| `sleep_efficiency_7day_avg` | `sleep_efficiency_7d_avg` | 直接 (%) |

### weekly CSV → weekly_health_summary 字段映射

| CSV 列名 | DB 字段 | 转换 |
|----------|---------|------|
| `week_start` | `week_start` | str → date |
| `steps_total` | `steps_total` | 直接 |
| `steps_daily_avg` | `steps_daily_avg` | 直接 |
| `active_energy_kcal_total` | `active_energy_total` | **重命名** |
| `active_energy_kcal_daily_avg` | `active_energy_daily_avg` | **重命名** |
| `basal_energy_kcal_total` | `basal_energy_total` | **重命名** |
| `distance_km_total` | `distance_total` | **重命名** |
| `distance_km_daily_avg` | `distance_daily_avg` | **重命名** |
| `exercise_minutes_total` | `exercise_minutes_total` | 直接 |
| `stand_hours_total` | `stand_hours_total` | 直接 |
| `body_mass_kg_avg` | `body_mass_avg` | **重命名** |
| `resting_hr_bpm_avg` | `resting_hr_avg` | **重命名** |
| `hrv_ms_avg` | `hrv_avg` | **重命名** |
| `vo2_max_avg` | `vo2_max_avg` | 直接 |
| `days_in_week` | `valid_days` | **重命名** |

### workout CSV → workout_records 字段映射

| CSV 列名 | DB 字段 | 转换 |
|----------|---------|------|
| `workout_type` | `workout_type` | 直接 |
| `duration_minutes` | `duration` | 直接 (均为分钟) |
| `distance_km` | `distance` | 直接 (均为km) |
| `energy_kcal` | `calories` | **重命名** |
| `start_time` | `start_time` | str → datetime |
| *(固定值)* | `source` | `"apple_health"` |

---

## 单位速查

| 指标类别 | 字段 | 单位 |
|---------|------|------|
| 距离 | `distance_km`, `distance`, `distance_total` | **km** |
| 时长 (运动) | `exercise_minutes`, `duration` | **分钟** |
| 时长 (睡眠) | `in_bed_minutes`, `asleep_minutes`, `awake_minutes` | **分钟** |
| 时长 (睡眠) | `sleep_duration_hours` | **小时** |
| 时长 (7日睡眠) | `sleep_7d_avg` | **分钟** |
| 时长 (深睡) | `deep_sleep_minutes` | **分钟** |
| 能量 | `active_energy_kcal`, `basal_energy_kcal`, `calories` | **kcal** |
| 体重 | `body_mass_kg`, `weight_7d_avg`, `body_mass_avg` | **kg** |
| 心率 | `resting_hr_bpm`, `resting_hr_7d_avg`, `heart_rate_avg/max` | **bpm** |
| HRV | `hrv_ms`, `hrv_7d_avg`, `hrv_avg` | **ms** |
| VO2Max | `vo2_max`, `vo2_max_avg` | **ml/kg/min** |
| 百分比 | `body_fat_pct`, `sleep_efficiency`, `sleep_efficiency_7d_avg` | **%** |
| 站立 | `stand_hours` | **小时** |
