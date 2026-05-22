# 数据库 Schema 适配变更说明

> 基于 apple-health-processor 算法简化，列出 `health_data.db` 需要同步修改的内容。
> 
> 数据库模型源文件: `assistant/src/storage/models/health_data.py`

---

## 一、daily_health_summary 表

### 1.1 删除字段

| 字段 | 原类型 | 原说明 | 删除原因 |
|------|--------|--------|----------|
| `data_completeness` | str | `complete` / `partial` / `incomplete` / `invalid` | 已移除四级分类逻辑 |
| `data_quality_score` | float | 0-100 | 已移除质量评分算法 |

### 1.2 修改字段

| 字段 | 修改内容 |
|------|---------|
| `wear_status` | 值域从 `full_day` / `partial_day` / `not_worn` / `unknown` 简化为 **`worn` / `not_worn`**。判定逻辑：`stand_hours > 0 OR active_energy_kcal > 0` → `worn`，否则 → `not_worn` |
| `sleep_7d_avg` | 单位从 **小时** 改为 **分钟**，与 `asleep_minutes` 保持一致 |

### 1.3 重命名字段

| 旧字段 | 新字段 | 说明 |
|--------|--------|------|
| `is_sedentary_day` | `is_low_activity_day` | 语义更准确：steps < 1000 且 wear_status == "worn" |

### 1.4 新增字段

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `deep_sleep_minutes` | float? | 分钟 | 深度睡眠时长（Apple Watch 数据才有，可能为空） |

### 1.5 修改后的完整字段列表

```
id                    int          主键
record_date           date         记录日期 (唯一约束)

-- 活动指标
steps                 int          步
active_energy_kcal    float        kcal
basal_energy_kcal     float        kcal
distance_km           float        km
exercise_minutes      float        分钟
stand_hours           int          小时

-- 身体指标
body_mass_kg          float?       kg
body_fat_pct          float?       %
muscle_mass_kg        float?       kg
resting_hr_bpm        float?       bpm
hrv_ms                float?       ms
vo2_max               float?       ml/kg/min

-- 睡眠指标
bed_time              datetime?    入床时间 (含时区)
wake_time             datetime?    起床时间 (含时区)
in_bed_minutes        int?         分钟
asleep_minutes        int?         分钟
deep_sleep_minutes    float?       分钟  ← 新增
awake_minutes         int?         分钟
sleep_efficiency      float?       %
sleep_duration_hours  float?       小时

-- 数据质量
wear_status           str          "worn" / "not_worn"  ← 简化
is_low_activity_day   bool         ← 重命名自 is_sedentary_day

-- 7日滚动指标
weight_7d_avg         float?       kg
steps_7d_avg          float?       步
resting_hr_7d_avg     float?       bpm
hrv_7d_avg            float?       ms
exercise_7d_total     float?       分钟
sleep_7d_avg          float?       分钟  ← 单位从小时改为分钟

-- 元数据
data_source           str          "manual" / "apple_health"
created_at            datetime
updated_at            datetime
```

---

## 二、weekly_health_summary 表

### 2.1 删除字段

| 字段 | 原类型 | 删除原因 |
|------|--------|----------|
| `avg_quality_score` | float (0-100) | 已移除质量评分 |

### 2.2 无新增字段

其余字段不变。

---

## 三、workout_records 表

### 3.1 新增字段映射

processor 已新增输出，DB 映射需同步：

| CSV 列名 | DB 字段 | 转换 |
|----------|---------|------|
| `heart_rate_avg` | `heart_rate_avg` | 直接 (float?, bpm) |
| `heart_rate_max` | `heart_rate_max` | 直接 (float?, bpm) |

---

## 四、CSV 导入映射变更

### 4.1 daily CSV 映射变更

| 变更 | CSV 列名 | DB 字段 | 说明 |
|------|----------|---------|------|
| 删除 | `data_completeness` | `data_completeness` | 不再输出 |
| 删除 | `data_quality_score` | `data_quality_score` | 不再输出 |
| 重命名 | `is_sedentary_day` | `is_low_activity_day` | 语义更新 |
| 新增 | `body_fat_pct` | `body_fat_pct` | 新增输出 |
| 新增 | `muscle_mass_kg` | `muscle_mass_kg` | 新增输出 |

### 4.2 sleep CSV 映射变更

| 变更 | CSV 列名 | DB 字段 | 说明 |
|------|----------|---------|------|
| 新增 | `deep_sleep_minutes` | `deep_sleep_minutes` | 直接 |

### 4.3 weekly CSV 映射变更

| 变更 | CSV 列名 | DB 字段 | 说明 |
|------|----------|---------|------|
| 新增 | `distance_daily_avg` | `distance_daily_avg` | 直接 |

---

## 五、单位速查变更

| 变更 | 字段 | 旧单位 | 新单位 |
|------|------|--------|--------|
| 修改 | `sleep_7d_avg` | 小时 | **分钟** |
| 新增 | `deep_sleep_minutes` | - | 分钟 |

移除：
- `data_quality_score` 行（已删除该字段）

---

## 六、迁移 SQL 参考

```sql
-- 1. daily_health_summary
ALTER TABLE daily_health_summary ADD COLUMN deep_sleep_minutes FLOAT;
ALTER TABLE daily_health_summary ADD COLUMN is_low_activity_day BOOLEAN;
ALTER TABLE daily_health_summary DROP COLUMN data_completeness;
ALTER TABLE daily_health_summary DROP COLUMN data_quality_score;
ALTER TABLE daily_health_summary DROP COLUMN is_sedentary_day;

-- 更新 wear_status 值域
UPDATE daily_health_summary SET wear_status = 'worn' WHERE wear_status IN ('full_day', 'partial_day');
UPDATE daily_health_summary SET wear_status = 'not_worn' WHERE wear_status IN ('not_worn', 'unknown');

-- sleep_7d_avg 单位转换: 小时 → 分钟 (如有存量数据)
UPDATE daily_health_summary SET sleep_7d_avg = sleep_7d_avg * 60 WHERE sleep_7d_avg IS NOT NULL;

-- 2. weekly_health_summary
ALTER TABLE weekly_health_summary DROP COLUMN avg_quality_score;

-- 3. workout_records (如尚未有这两个字段)
ALTER TABLE workout_records ADD COLUMN heart_rate_avg FLOAT;
ALTER TABLE workout_records ADD COLUMN heart_rate_max FLOAT;
```

> **注意**: SQLite 不支持 `DROP COLUMN`（3.35.0 之前版本）。如需兼容旧版 SQLite，需重建表。
