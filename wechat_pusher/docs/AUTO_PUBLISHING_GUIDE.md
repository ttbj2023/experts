# 微信公众号自动发布使用指南

## 🎯 功能说明

完整自动化工作流：从Markdown文章到微信公众号草稿箱

**核心功能**：
- ✅ AI自动生成摘要（50字/120字符）
- ✅ AI自动生成配图提示词（封面2个 + 插图3-4个）
- ✅ AI自动分析图表需求
- ✅ 自动生成封面图、插图、图表
- ✅ 自动上传素材到微信
- ✅ 自动转换为微信HTML（嵌入图片）
- ✅ 自动创建草稿

---

## 📋 前置要求

### 1. 配置微信API

编辑 `.env` 文件，填入你的微信公众号信息：

```bash
# 微信公众号配置
WECHAT_APPID=your_appid_here
WECHAT_SECRET=your_secret_here
```

**获取方式**：
1. 登录微信公众平台：https://mp.weixin.qq.com
2. 进入「开发」→「基本配置」
3. 查看「开发者ID」（AppID）
4. 生成并查看「开发者密码」（AppSecret）

### 2. 配置固定作者（可选）

在 `.env` 中设置默认作者：

```bash
# 微信文章配置
DEFAULT_AUTHOR=你的名字
```

或通过命令行参数指定：`--author "作者名"`

### 3. 确认AI配置

确保 `.env` 中的AI配置正确：

```bash
# DeepSeek AI（文本生成）
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-reasoner

# Doubao AI（图片生成）
DOUBAO_API_KEY=xxx
DOUBAO_MODEL=doubao-seedream-4-5-251128
```

---

## 🚀 使用方法

### 基础用法

```bash
# 发布文章（使用默认作者）
wechat-pusher publish article.md

# 指定作者
wechat-pusher publish article.md --author "张三"
```

### Markdown文件格式要求

**必需**：
- 文章标题（第一行使用 `# 标题`）
- 文章正文内容

**示例**（`article.md`）：
```markdown
# 2025年人工智能发展趋势

人工智能正在深刻改变各个行业。在医疗领域，AI辅助诊断...
（更多内容）
```

---

## 🔄 完整工作流程

```
1. 解析Markdown
   ├─ 提取标题（第一个#标题）
   └─ 提取正文内容

2. AI分析（DeepSeek Reasoner）
   ├─ 生成摘要（50字/120字符）
   ├─ 生成配图提示词
   │  ├─ 封面图提示词 × 2
   │  └─ 插图提示词 × 3-4
   ├─ 分析图表需求
   └─ 优化文章内容

3. 生成资源
   ├─ Doubao生成封面图（3840×1632）× 2
   ├─ Doubao生成插图（3072×1898）× 3-4
   └─ Matplotlib生成图表（如需要）

4. 上传素材到微信
   ├─ 上传封面图 → 获取media_id
   ├─ 上传插图 → 获取media_id列表
   └─ 上传图表 → 获取media_id

5. 转换HTML
   ├─ Markdown → HTML
   ├─ 嵌入图片（使用media_id）
   └─ 微信规范适配（过滤标签/样式）

6. 创建草稿
   └─ 上传到草稿箱 → 返回草稿ID
```

---

## 📊 输出说明

### 1. 临时文件

生成的图片和资源保存在：
```
output/
└── {timestamp}/           # 每篇文章的独立目录
    ├── cover_1.png        # 封面图选项1
    ├── cover_2.png        # 封面图选项2
    ├── illustration_1.png # 插图
    ├── illustration_2.png
    └── chart.png          # 图表（如需要）
```

### 2. 草稿位置

草稿会自动保存到你的微信公众号后台：
- 登录 https://mp.weixin.qq.com
- 进入「草稿箱」
- 找到自动创建的草稿

### 3. 日志文件

详细日志保存在：
```
logs/wechat_pusher.log
```

---

## 💡 使用示例

### 示例1：发布技术文章

```bash
# 文件：tech_article.md
# 内容：
# Python异步编程完全指南

Python 3.5引入了async/await语法...

# 执行发布
wechat-pusher publish tech_article.md --author "技术宅"
```

**输出结果**：
- ✅ 摘要：`"Python异步编程完全指南：深入理解async/await语法、协程原理..." (45字符)`
- ✅ 封面图：2张（科技风格）
- ✅ 插图：3张（代码示例图解）
- ✅ 草稿已创建

### 示例2：发布财经文章

```bash
# 文件：finance.md
# 内容：
# 2025年全球宏观经济展望

随着美联储政策调整...

wechat-pusher publish finance.md
```

**AI自动分析**：
- ✅ 检测到数据内容
- ✅ 生成经济趋势图表
- ✅ 生成专业配图

---

## ⚙️ 高级配置

### 自定义生成图片数量

修改 `src/workflow/publisher.py`:

```python
# 生成封面图（改为3个）
result["cover_prompts"] = prompts.get("cover_prompts", [])[:3]

# 生成插图（改为5个）
result["image_prompts"] = prompts.get("image_prompts", [])[:5]
```

### 调整图片嵌入位置

修改 `_embed_images()` 方法：

```python
def _embed_images(self, html: str, media_ids: Dict[str, List[str]]) -> str:
    # 自定义图片插入逻辑
    # 例如：在h2标题后插入插图
    ...
```

---

## ⚠️ 注意事项

### 1. 微信API限制

- **素材上传限制**：永久素材总数限制10万
- **草稿数量**：草稿箱总数限制10万
- **API调用频率**：每日有调用次数限制

### 2. 图片生成时间

- 封面图：约10-15秒/张
- 插图：约10-15秒/张
- 总耗时：约1-2分钟（取决于图片数量）

### 3. 网络要求

- 需要稳定的网络连接
- 需要能访问：
  - DeepSeek API: `https://api.deepseek.com`
  - Volcengine API: `https://ark.cn-beijing.volces.com`
  - 微信API: `https://api.weixin.qq.com`

### 4. 错误处理

如果发布失败：
1. 查看 `logs/wechat_pusher.log` 了解详细错误
2. 检查网络连接
3. 确认API配置正确
4. 检查微信API调用额度

---

## 🐛 常见问题

### Q1: 提示"获取access_token失败"

**原因**：AppID或Secret配置错误

**解决**：
1. 检查 `.env` 中的 `WECHAT_APPID` 和 `WECHAT_SECRET`
2. 确认在微信后台正确获取了这些信息
3. 确认IP地址在白名单中

### Q2: 图片上传失败

**原因**：
- 网络连接问题
- 图片格式问题
- API额度不足

**解决**：
1. 检查网络连接
2. 确认图片为PNG格式
3. 查看微信API调用次数

### Q3: 草稿创建成功但图片未显示

**原因**：media_id嵌入错误

**解决**：
1. 查看日志中的media_id
2. 确认图片上传成功
3. 手动在微信后台检查图片素材库

### Q4: AI生成内容超时

**原因**：
- API响应慢
- 文章内容过长
- 网络问题

**解决**：
1. 增加超时时间（修改配置）
2. 分段处理长文章
3. 检查网络连接

---

## 📈 性能优化

### 加速图片生成

```python
# 在 src/workflow/publisher.py 中添加并发
import concurrent.futures

def generate_images_parallel(self, prompts):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 并发生成图片
        futures = []
        for prompt in prompts:
            future = executor.submit(doubao_client.generate_image, prompt)
            futures.append(future)
        # 等待完成
        results = [f.result() for f in futures]
    return results
```

### 缓存AI分析结果

```python
# 保存AI分析结果到文件
import json

def save_ai_result(article_id, result):
    with open(f"output/{article_id}/ai_result.json", "w") as f:
        json.dump(result, f, ensure_ascii=False)

def load_ai_result(article_id):
    try:
        with open(f"output/{article_id}/ai_result.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
```

---

## 🎉 最佳实践

### 1. Markdown写作建议

```markdown
# 文章标题（简短有力）

## 第一部分

引言内容...

## 第二部分

正文内容...

### 数据示例

- 数据1: 100
- 数据2: 200
- 数据3: 300

AI会自动识别并生成图表！
```

### 2. 标题优化

- 标题要简洁（建议<30字）
- 突出核心价值
- 包含关键词

### 3. 内容结构

- 使用小标题分段
- 适当使用列表
- 重要数据突出显示

### 4. 发布前检查

```bash
# 1. 预览HTML（可选）
wechat-pusher convert article.md -o preview.html

# 2. 验证HTML
wechat-pusher validate preview.html

# 3. 发布到草稿
wechat-pusher publish article.md

# 4. 在微信后台检查
# - 登录 mp.weixin.qq.com
# - 进入草稿箱
# - 预览文章
# - 检查图片显示
# - 编辑调整
# - 发布
```

---

## 📞 技术支持

### 查看日志

```bash
# 查看完整日志
cat logs/wechat_pusher.log

# 实时监控日志
tail -f logs/wechat_pusher.log

# 查看错误日志
grep ERROR logs/wechat_pusher.log
```

### 调试模式

```bash
# 设置日志级别为DEBUG
export LOG_LEVEL=DEBUG

wechat-pusher publish article.md
```

---

## 🔄 版本更新

**当前版本**: v1.0.0

**新功能**：
- ✅ 完整自动化工作流
- ✅ AI智能分析
- ✅ 自动生成配图
- ✅ 自动创建草稿

**计划功能**：
- ⏳ 支持视频上传
- ⏳ 支持语音上传
- ⏳ 批量发布
- ⏳ 定时发布

---

**最后更新**: 2025-02-19
**文档版本**: v1.0.0
