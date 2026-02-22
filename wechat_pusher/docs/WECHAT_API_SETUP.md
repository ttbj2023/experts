# 微信公众号API配置指南

## 🌐 你的服务器信息

```
公网IP: 144.34.186.22
位置: 美国加利福尼亚州洛杉矶
主机名: 144.34.186.22.16clouds.com
```

---

## 📋 完整配置步骤

### 步骤1：获取微信公众号凭证

#### 1.1 登录微信公众平台

访问：https://mp.weixin.qq.com

使用你的公众号管理员账号扫码登录

#### 1.2 进入基本配置

1. 点击左侧菜单「开发」→「基本配置」
2. 找到「开发者ID（AppID）」
3. 找到「开发者密码（AppSecret）」

**示例**：
```
AppID: wx1234567890abcdef
AppSecret: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**注意**：
- AppSecret是保密的，不要泄露
- 如果重置了AppSecret，旧密钥会立即失效
- 建议定期更换密钥

---

### 步骤2：配置IP白名单

#### 2.1 找到IP白名单配置

在「基本配置」页面，向下滚动找到「服务器配置」部分

你会看到「IP白名单」配置框

#### 2.2 添加你的服务器IP

点击「配置」，在弹出的对话框中输入：
```
144.34.186.22
```

**注意事项**：
- 一行一个IP，不要有空格
- 点击「确定」保存
- 配置后立即生效（通常5分钟内）

#### 2.3 验证IP白名单

运行测试脚本：
```bash
python test_wechat_api.py
```

如果成功，会显示：
```
✅ access_token获取成功！
Token长度: 115字符
Token预览: 67_xxxxxxxxxxxxxxxxxxxx...
```

如果失败，会显示：
```
❌ access_token获取失败

可能的原因:
   1. IP白名单未配置
   2. AppID或Secret配置错误
```

---

### 步骤3：配置项目环境变量

#### 3.1 编辑.env文件

在项目根目录找到 `.env` 文件，编辑以下配置：

```bash
# ==================== 微信公众号配置 ====================
WECHAT_APPID=wx1234567890abcdef  # 替换为你的真实AppID
WECHAT_SECRET=your_real_secret_here  # 替换为你的真实Secret
WECHAT_TOKEN_EXPIRE=7200
```

#### 3.2 保存文件

保存并关闭 `.env` 文件

#### 3.3 验证配置

```bash
# 查看配置是否正确
cat .env | grep WECHAT

# 应该看到你的真实AppID和Secret，不是默认值
```

---

### 步骤4：测试API连接

#### 4.1 运行测试脚本

```bash
python test_wechat_api.py
```

#### 4.2 预期输出

如果配置正确，会看到：
```
================================================================================
🧪 测试微信API连接
================================================================================

📋 当前配置:
   AppID: wx1234567890abcdef
   Base URL: https://api.weixin.qq.com

✅ 配置检查通过

================================================================================
🔑 测试获取access_token
================================================================================

⏳ 正在获取access_token...
✅ access_token获取成功！
   Token长度: 115字符
   Token预览: 67_xxxxxxxxxxxxxxxxxxxx...

🎉 微信API连接测试成功！

💡 接下来可以:
   1. 运行完整发布流程: wechat-pusher publish article.md
   2. 测试素材上传功能
   3. 测试草稿创建功能
```

#### 4.3 错误处理

**错误1: IP白名单未配置**
```
❌ access_token获取失败
错误代码: 40164
错误信息: invalid ip 144.34.186.22, not in whitelist
```

**解决方案**：
1. 登录微信公众平台
2. 进入「开发」→「基本配置」
3. 在IP白名单中添加：`144.34.186.22`

**错误2: AppID或Secret错误**
```
❌ access_token获取失败
错误代码: 40164
错误信息: invalid appid
```

**解决方案**：
1. 检查 `.env` 文件中的 `WECHAT_APPID`
2. 检查 `.env` 文件中的 `WECHAT_SECRET`
3. 确认没有多余的空格或引号

**错误3: 网络连接问题**
```
❌ 测试失败: Connection timeout
```

**解决方案**：
1. 检查网络连接
2. 确认能访问 `api.weixin.qq.com`
3. 检查防火墙设置

---

## 🔧 高级配置

### 配置多个IP（如果需要）

如果你的服务器有多个公网IP，可以全部添加：

```
144.34.186.22
144.34.186.23
144.34.186.24
```

### 查看当前IP白名单

如果忘记配置了哪些IP，可以：

1. 登录微信公众平台
2. 进入「开发」→「基本配置」
3. 查看「IP白名单」显示框

### 重置AppSecret

如果怀疑密钥泄露：

1. 在「基本配置」页面
2. 点击「重置」AppSecret
3. 验证身份（扫码）
4. 生成新的密钥
5. **重要**: 立即更新 `.env` 文件中的 `WECHAT_SECRET`

---

## 📊 API限制说明

### 调用频率限制

微信公众号API有调用频率限制：

| API | 限制 |
|-----|------|
| 获取access_token | 每日1000次 |
| 上传素材 | 每日1000次 |
| 创建草稿 | 每日100次 |

### Token有效期

- **有效期**: 7200秒（2小时）
- **缓存策略**: 系统会自动缓存token
- **自动刷新**: token过期前5分钟自动刷新

---

## 🧪 完整测试流程

### 测试1：API连接

```bash
python test_wechat_api.py
```

### 测试2：素材上传

```bash
python -c "
from src.wechat.api_client import wechat_api_client
media_id = wechat_api_client.upload_media('bitcoin_article_draft.md', 'image')
print(f'Media ID: {media_id}')
"
```

### 测试3：完整发布流程

```bash
wechat-pusher publish bitcoin_article_draft.md
```

---

## ⚠️ 常见问题

### Q1: IP白名单配置后还是提示"invalid ip"

**原因**: IP白名单生效需要5分钟左右

**解决**:
1. 等待5-10分钟
2. 重新运行测试脚本
3. 如果还是失败，确认IP地址正确（无多余空格）

### Q2: 如何确认我的公网IP？

**方法1**:
```bash
curl -s ifconfig.me
```

**方法2**: 访问 https://ipinfo.io

**方法3**: 运行测试脚本（会自动显示）

### Q3: AppSecret在哪里生成？

**步骤**:
1. 登录微信公众平台
2. 进入「开发」→「基本配置」
3. 找到「开发者密码（AppSecret）」
4. 如果从未设置，点击「重置」
5. 扫码验证身份
6. 复制生成的密钥

### Q4: 为什么需要配置IP白名单？

**原因**:
- 安全考虑，防止未授权访问
- 微信只允许白名单内的IP调用API
- 保护你的公众号数据安全

### Q5: 可以使用域名代替IP吗？

**不可以**:
- 微信只接受IP地址
- 不支持域名
- 不支持通配符

---

## 🎯 下一步

配置完成后，你可以：

1. **测试API连接**
   ```bash
   python test_wechat_api.py
   ```

2. **测试素材上传**
   ```bash
   # 上传测试图片
   python -c "
   from src.wechat.api_client import wechat_api_client
   media_id = wechat_api_client.upload_media('test.png', 'image')
   print(f'上传成功，Media ID: {media_id}')
   "
   ```

3. **完整发布流程**
   ```bash
   wechat-pusher publish article.md
   ```

4. **查看草稿**
   - 登录 https://mp.weixin.qq.com
   - 进入「草稿箱」
   - 查看自动创建的草稿

---

## 📞 技术支持

如果遇到问题：

1. **查看日志**
   ```bash
   tail -f logs/wechat_pusher.log
   ```

2. **检查配置**
   ```bash
   cat .env | grep WECHAT
   ```

3. **验证IP**
   ```bash
   curl -s ifconfig.me
   ```

4. **测试网络**
   ```bash
   ping api.weixin.qq.com
   ```

---

**配置完成后，系统会自动处理：**
- ✅ Token自动刷新
- ✅ 素材上传
- ✅ 草稿创建
- ✅ 错误重试

**更新时间**: 2025-02-19
**文档版本**: v1.0.0
