# API开发指南
## DataFlow 实时数据处理平台

**版本**：v2.1.0
**最后更新**：2024-12-15
**维护团队**：平台架构组

---

## 快速开始

### 环境要求

- Python 3.8+
- Redis 6.0+
- PostgreSQL 13+
- Docker & Docker Compose

### 安装

```bash
# 克隆仓库
git clone https://github.com/dataflow/platform.git
cd platform

# 安装依赖
pip install -r requirements.txt

# 启动服务
docker-compose up -d

# 初始化数据库
python scripts/init_db.py

# 启动API服务
python api/app.py
```

### 验证安装

```bash
curl http://localhost:8080/api/v1/health
```

预期返回：

```json
{
  "status": "ok",
  "version": "2.1.0",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

---

## 目录

- [快速开始](#快速开始)
- [概述](#概述)
- [认证](#认证)
- [API端点](#api端点)
  - [数据流管理](#数据流管理)
  - [任务管理](#任务管理)
  - [监控指标](#监控指标)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)
- [FAQ](#faq)

---

## 概述

DataFlow平台提供RESTful API，支持实时数据流的创建、管理和监控。API基于HTTP/HTTPS协议，使用JSON格式交换数据。

### 基础URL

- **生产环境**：`https://api.dataflow.io/api/v1`
- **测试环境**：`https://api-test.dataflow.io/api/v1`
- **本地开发**：`http://localhost:8080/api/v1`

### 请求格式

所有API端点遵循以下格式：

```
METHOD /api/v1/{resource}/{id}?query=params
```

**示例**：

```
GET /api/v1/streams/123?include=metadata
```

---

## 认证

### API密钥认证

所有API请求需要在HTTP Header中包含API密钥：

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### 获取API密钥

1. 登录控制台：https://console.dataflow.io
2. 进入"API管理"页面
3. 点击"创建密钥"
4. 复制生成的密钥（仅显示一次）

### 密钥权限

| 密钥类型 | 权限范围 | 有效期 |
|----------|----------|--------|
| **只读密钥** | GET操作 | 永久 |
| **读写密钥** | GET, POST, PUT | 永久 |
| **临时密钥** | 所有操作 | 24小时 |

> ⚠️ **注意**：请妥善保管API密钥，不要在客户端代码中硬编码。

---

## API端点

### 数据流管理

#### 创建数据流

**端点**：`POST /streams`

**请求体**：

```json
{
  "name": "user-events",
  "description": "用户行为事件流",
  "source": {
    "type": "kafka",
    "config": {
      "bootstrap_servers": "kafka1:9092",
      "topic": "user.events",
      "group_id": "processor-1"
    }
  },
  "sink": {
    "type": "elasticsearch",
    "config": {
      "hosts": ["es1:9200"],
      "index": "user-events-%{yyyy.MM.dd}"
    }
  },
  "transform": {
    "type": "sql",
    "query": "SELECT * FROM events WHERE type = 'click'"
  },
  "options": {
    "parallelism": 4,
    "checkpoint_interval": 60000
  }
}
```

**响应**：`201 Created`

```json
{
  "id": "str_abc123xyz",
  "name": "user-events",
  "status": "created",
  "created_at": "2024-12-15T10:30:00Z",
  "links": {
    "self": "/api/v1/streams/str_abc123xyz",
    "start": "/api/v1/streams/str_abc123xyz/start",
    "monitor": "/api/v1/streams/str_abc123xyz/metrics"
  }
}
```

**错误响应**：`400 Bad Request`

```json
{
  "error": {
    "code": "INVALID_SOURCE_TYPE",
    "message": "不支持的数据源类型: xyz",
    "details": {
      "supported_types": ["kafka", "rabbitmq", "pulsar"]
    }
  }
}
```

#### 获取数据流列表

**端点**：`GET /streams`

**查询参数**：

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| page | integer | 否 | 页码（默认1） |
| size | integer | 否 | 每页数量（默认20） |
| status | string | 否 | 状态筛选 |
| sort | string | 否 | 排序字段 |

**请求示例**：

```bash
curl -H "Authorization: Bearer YOUR_KEY" \
  "https://api.dataflow.io/api/v1/streams?page=1&size=10&status=running"
```

**响应**：`200 OK`

```json
{
  "data": [
    {
      "id": "str_abc123",
      "name": "user-events",
      "status": "running",
      "throughput": 15234.5,
      "latency_ms": 45.2
    }
  ],
  "pagination": {
    "page": 1,
    "size": 10,
    "total": 156,
    "total_pages": 16
  }
}
```

#### 启动数据流

**端点**：`POST /streams/{stream_id}/start`

**路径参数**：

- `stream_id`（string）：数据流ID

**请求示例**：

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_KEY" \
  https://api.dataflow.io/api/v1/streams/str_abc123/start
```

**响应**：`200 OK`

```json
{
  "id": "str_abc123",
  "status": "starting",
  "message": "数据流正在启动，预计30秒后进入运行状态"
}
```

#### 停止数据流

**端点**：`POST /streams/{stream_id}/stop`

**请求示例**：

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_KEY" \
  https://api.dataflow.io/api/v1/streams/str_abc123/stop
```

**响应**：`200 OK`

```json
{
  "id": "str_abc123",
  "status": "stopped",
  "stopped_at": "2024-12-15T11:00:00Z",
  "statistics": {
    "processed_records": 1523467,
    "uptime_seconds": 3600
  }
}
```

#### 删除数据流

**端点**：`DELETE /streams/{stream_id}`

**请求示例**：

```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_KEY" \
  https://api.dataflow.io/api/v1/streams/str_abc123
```

**响应**：`204 No Content`

---

### 任务管理

#### 提交任务

**端点**：`POST /tasks`

**请求体**：

```json
{
  "type": "batch_analytics",
  "name": "daily_report",
  "config": {
    "input_path": "s3://data/events/2024-12-15/*",
    "output_path": "s3://reports/daily/2024-12-15",
    "sql": "SELECT date, COUNT(*) as cnt FROM events GROUP BY date"
  },
  "schedule": {
    "type": "cron",
    "expression": "0 2 * * *"
  }
}
```

**响应**：`201 Created`

```json
{
  "task_id": "task_xyz789",
  "status": "pending",
  "scheduled_at": "2024-12-15T02:00:00Z",
  "created_at": "2024-12-15T10:30:00Z"
}
```

#### 获取任务状态

**端点**：`GET /tasks/{task_id}`

**响应**：`200 OK`

```json
{
  "task_id": "task_xyz789",
  "status": "running",
  "progress": 0.65,
  "started_at": "2024-12-15T02:00:00Z",
  "estimated_completion": "2024-12-15T02:15:00Z",
  "metrics": {
    "records_processed": 6500000,
    "records_total": 10000000,
    "error_rate": 0.001
  }
}
```

#### 取消任务

**端点**：`POST /tasks/{task_id}/cancel`

**响应**：`200 OK`

```json
{
  "task_id": "task_xyz789",
  "status": "cancelled",
  "cancelled_at": "2024-12-15T10:35:00Z",
  "progress": 0.65
}
```

---

### 监控指标

#### 获取流指标

**端点**：`GET /streams/{stream_id}/metrics`

**查询参数**：

- `start`（timestamp）：开始时间
- `end`（timestamp）：结束时间
- `granularity`（string）：粒度（`minute` | `hour` | `day`）

**请求示例**：

```bash
curl -H "Authorization: Bearer YOUR_KEY" \
  "https://api.dataflow.io/api/v1/streams/str_abc123/metrics?start=1702617600&end=1702704000&granularity=hour"
```

**响应**：`200 OK`

```json
{
  "stream_id": "str_abc123",
  "metrics": [
    {
      "timestamp": "2024-12-15T00:00:00Z",
      "throughput_rps": 15234.5,
      "latency_ms": 45.2,
      "error_rate": 0.001,
      "cpu_usage": 0.65
    },
    {
      "timestamp": "2024-12-15T01:00:00Z",
      "throughput_rps": 16892.3,
      "latency_ms": 42.8,
      "error_rate": 0.0008,
      "cpu_usage": 0.72
    }
  ]
}
```

#### 系统健康检查

**端点**：`GET /health`

**响应**：`200 OK`

```json
{
  "status": "healthy",
  "components": {
    "api": "ok",
    "database": "ok",
    "cache": "ok",
    "message_queue": "ok"
  },
  "version": "2.1.0"
}
```

---

## 数据模型

### 数据流对象

```typescript
interface Stream {
  id: string;                    // 唯一标识符
  name: string;                  // 名称
  description?: string;          // 描述
  status: StreamStatus;          // 状态
  source: DataSource;            // 数据源配置
  sink: DataSink;                // 数据目标配置
  transform?: Transform;         // 转换规则
  options: StreamOptions;        // 选项
  created_at: string;            // 创建时间
  updated_at: string;            // 更新时间
}

type StreamStatus =
  | "created"    // 已创建
  | "starting"   // 启动中
  | "running"    // 运行中
  | "stopping"   // 停止中
  | "stopped"    // 已停止
  | "failed";    // 失败

interface DataSource {
  type: "kafka" | "rabbitmq" | "pulsar";
  config: Record<string, any>;
}

interface DataSink {
  type: "elasticsearch" | "mongodb" | "s3";
  config: Record<string, any>;
}
```

### 任务对象

```typescript
interface Task {
  task_id: string;
  type: string;
  name: string;
  status: TaskStatus;
  config: Record<string, any>;
  schedule?: Schedule;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

type TaskStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";
```

---

## 错误处理

### 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": {},
    "request_id": "req_abc123"
  }
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 描述 |
|-----------|--------|------|
| 400 | `INVALID_REQUEST` | 请求参数无效 |
| 401 | `UNAUTHORIZED` | 未授权，API密钥无效 |
| 403 | `FORBIDDEN` | 权限不足 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` | 资源冲突 |
| 429 | `RATE_LIMIT_EXCEEDED` | 超过速率限制 |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 |
| 503 | `SERVICE_UNAVAILABLE` | 服务不可用 |

### 错误处理示例

**Python**：

```python
import requests

try:
    response = requests.post(
        "https://api.dataflow.io/api/v1/streams",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=stream_config,
        timeout=10
    )
    response.raise_for_status()
    return response.json()

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("API密钥无效")
    elif e.response.status_code == 429:
        print("超过速率限制，请稍后重试")
    else:
        error_data = e.response.json()
        print(f"错误: {error_data['error']['message']}")
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
```

**JavaScript**：

```javascript
async function createStream(config) {
  try {
    const response = await fetch('https://api.dataflow.io/api/v1/streams', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }

    return await response.json();
  } catch (error) {
    console.error('创建数据流失败:', error.message);
    throw error;
  }
}
```

---

## 最佳实践

### 1. 连接管理

```python
# ✅ 推荐：使用连接池
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
session.mount('https://', adapter)

# ❌ 不推荐：每次创建新连接
response = requests.get(url)  # 避免这样做
```

### 2. 批量操作

```python
# ✅ 推荐：批量提交
streams = [stream1, stream2, stream3]
responses = await asyncio.gather(*[
    create_stream(s) for s in streams
])

# ❌ 不推荐：顺序提交
for stream in streams:
    create_stream(stream)  # 串行，效率低
```

### 3. 错误重试

```python
# ✅ 推荐：指数退避重试
import time

def retry_request(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)
```

### 4. 监控告警

```python
# 实时监控流状态
def monitor_stream(stream_id):
    while True:
        metrics = get_stream_metrics(stream_id)
        if metrics['error_rate'] > 0.01:  # 错误率超过1%
            send_alert(f"流 {stream_id} 错误率过高")
        time.sleep(60)
```

---

## FAQ

### Q: API速率限制是多少？

**A**:
- 免费版：100次/分钟
- 专业版：1000次/分钟
- 企业版：无限制

### Q: 如何处理大文件上传？

**A**: 对于超过100MB的文件，建议使用分片上传：

```bash
# 1. 初始化上传
POST /uploads/init

# 2. 上传分片
POST /uploads/{upload_id}/part

# 3. 完成上传
POST /uploads/{upload_id}/complete
```

### Q: WebSocket支持吗？

**A**: 是的，我们提供WebSocket接口用于实时数据推送：

```javascript
const ws = new WebSocket('wss://api.dataflow.io/ws?token=YOUR_KEY');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('实时数据:', data);
};
```

### Q: 如何处理时区？

**A**: 所有时间戳使用ISO 8601格式，且为UTC时区：

```json
{
  "timestamp": "2024-12-15T10:30:00Z"
}
```

---

## 附录

### A. SDK列表

官方SDK：

- [Python SDK](https://github.com/dataflow/python-sdk)
- [JavaScript SDK](https://github.com/dataflow/js-sdk)
- [Java SDK](https://github.com/dataflow/java-sdk)
- [Go SDK](https://github.com/dataflow/go-sdk)

### B. 更新日志

**v2.1.0** (2024-12-15)
- 新增：批量操作API
- 改进：错误处理机制
- 修复：任务调度bug

**v2.0.0** (2024-11-01)
- 重大重构：API架构升级
- 新增：WebSocket支持
- 废弃：旧版认证方式

### C. 联系方式

- 技术支持：support@dataflow.io
- 问题反馈：https://github.com/dataflow/platform/issues
- 开发者社区：https://community.dataflow.io

---

**文档版本**：v2.1.0
**最后更新**：2024-12-15

---

> 💡 **提示**：订阅我们的[开发者通讯](https://dataflow.io/subscribe)，获取最新API更新和最佳实践。
