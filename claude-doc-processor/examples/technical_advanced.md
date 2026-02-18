# 技术文档高级样式展示

本文展示技术文档模板的所有高级样式功能。

---

## 1. 特殊提示框

技术文档常用提示框来强调重要信息。

### 注意提示框

> **注意：** 这是一个重要的提示信息。使用此样式来提醒读者注意某些关键点。

### 警告提示框

> **警告：** 这是一个警告信息。使用此样式来警示潜在的风险或问题。

### 错误提示框

> **错误：** 这是一个错误信息。使用此样式来展示错误状态或错误消息。

### 提示提示框

> **提示：** 这是一个有用的提示。使用此样式来提供额外的建议或最佳实践。

---

## 2. API端点样式

### 基本端点

<div class="api-endpoint">
  <span class="api-method api-method-GET">GET</span>
  <span class="api-path">/api/v1/users</span>
</div>

获取所有用户列表。

### 带描述的端点

<div class="api-endpoint">
  <span class="api-method api-method-POST">POST</span>
  <span class="api-path">/api/v1/users</span>
</div>

创建新用户。

**请求体**：
```json
{
  "name": "张三",
  "email": "zhangsan@example.com"
}
```

### 多种HTTP方法

<div class="api-endpoint">
  <span class="api-method api-method-PUT">PUT</span>
  <span class="api-path">/api/v1/users/:id</span>
</div>

更新用户信息。

---

<div class="api-endpoint">
  <span class="api-method api-method-DELETE">DELETE</span>
  <span class="api-path">/api/v1/users/:id</span>
</div>

删除用户。

---

<div class="api-endpoint">
  <span class="api-method api-method-PATCH">PATCH</span>
  <span class="api-path">/api/v1/users/:id</span>
</div>

部分更新用户信息。

---

## 3. 代码块样式

### 基础代码块

```python
def hello_world():
    print("Hello, World!")
    return True
```

### 带语言标签的代码块

<div class="code-language">JavaScript</div>

```javascript
function fetchData(url) {
  return fetch(url)
    .then(response => response.json())
    .then(data => console.log(data));
}
```

### 行内代码

使用 `Ctrl + C` 复制代码，使用 `Ctrl + V` 粘贴。

---

## 4. 键盘快捷键

按 `Ctrl + S` 保存文件。

按 `Ctrl + Shift + N` 打开新窗口。

使用 `Alt + Tab` 切换窗口。

---

## 5. 标签和徽章

### 普通标签

<span class="tag">Python</span>
<span class="tag">JavaScript</span>
<span class="tag">API</span>
<span class="tag">RESTful</span>

### 版本徽章

<span class="version-badge">v1.0.0</span>
<span class="version-badge">v2.1.0-beta</span>
<span class="version-badge">LATEST</span>

### 状态指示器

<span class="status status-success"></span> 成功
<span class="status status-warning"></span> 警告
<span class="status status-error"></span> 错误
<span class="status status-info"></span> 信息

---

## 6. 参数表格

### API参数表

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `user_id` | integer | 用户唯一标识符 |
| `name` | string | 用户名称 |
| `email` | string | 用户邮箱地址 |
| `role` | string | 用户角色（admin/user） |

### 请求头参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `Authorization` | string | Bearer token |
| `Content-Type` | string | application/json |
| `X-API-Key` | string | API密钥 |

---

## 7. 表格样式

### 基础表格

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |

### 带代码的表格

| 函数 | 语言 | 描述 |
|------|------|------|
| `print()` | Python | 输出到控制台 |
| `console.log()` | JavaScript | 输出到控制台 |
| `printf()` | C | 格式化输出 |

---

## 8. 列表样式

### 无序列表

- 第一项
- 第二项
  - 嵌套项1
  - 嵌套项2
- 第三项

### 有序列表

1. 第一步
2. 第二步
   1. 子步骤1
   2. 子步骤2
3. 第三步

### 任务列表（GitHub风格）

- [x] 已完成的任务
- [ ] 待完成的任务
- [x] 另一个已完成的任务

---

## 9. 链接样式

### 内部链接

查看[快速开始](#快速开始)部分。

### 外部链接

访问[GitHub](https://github.com)了解更多信息。

访问[Python官网](https://python.org)查看文档。

---

## 10. 文本格式

### 粗体和斜体

这是**粗体文本**，这是*斜体文本*，这是***粗斜体文本***。

### 高亮文本

这是`行内代码`，这是==高亮文本==。

### 删除线

这是~~删除线文本~~。

---

## 11. 水平分隔线

---

### 小分隔线

---

---

## 12. 图片和图片说明

![示例图片](https://via.placeholder.com/600x300)

**图1：示例图片说明**

---

## 13. 引用块

### 普通引用

> 这是一段引用文本。引用块通常用于引用其他文档或强调某段话。

### 嵌套引用

> 外层引用
>
> > 内层引用
>
> 回到外层引用

---

## 14. 数学公式

### 行内公式

行内公式：$E = mc^2$

### 块级公式

$$
f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}
$$

---

## 15. 综合示例

以下是一个综合了多种样式的示例：

> **注意：** 在使用API之前，请确保已经获取了有效的API密钥。

### 获取用户信息

<div class="api-endpoint">
  <span class="api-method api-method-GET">GET</span>
  <span class="api-path">/api/v1/users/:id</span>
</div>

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 用户ID |

**示例代码**：

```python
import requests

url = "https://api.example.com/users/123"
headers = {"Authorization": "Bearer your_token"}

response = requests.get(url, headers=headers)
user_data = response.json()

print(user_data)
```

**快捷键**：按 `Ctrl + C` 复制代码。

**返回状态**：
<span class="status status-success"></span> 成功：200 OK
<span class="status status-error"></span> 失败：404 Not Found

---

## 附录

### 版本历史

<span class="version-badge">v1.0.0</span> - 初始版本（2024-01-01）
<span class="version-badge">v1.1.0</span> - 添加新功能（2024-02-01）
<span class="version-badge">v2.0.0</span> - 重大更新（2024-03-01）

### 相关标签

<span class="tag">REST API</span>
<span class="tag">Python</span>
<span class="tag">JavaScript</span>
<span class="tag">文档</span>
