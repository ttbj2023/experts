# CLAUDE.md - 微信文章自动发布系统使用指南

## 项目定位

这是一个**使用型项目**，用于将Markdown格式的文章自动发布到微信公众号。

**核心流程**：获取Markdown文章 → AI优化内容 → 生成图表/插图 → 发布到微信

**重要**：本项目不需要开发代码，只需使用现有功能完成文章发布。

---

## 🚀 快速开始

### 基本使用流程

```bash
# 1. 准备Markdown文章（必须包含标题）
cat > my_article.md << 'EOF'
---
title: 文章标题
author: 作者名
---

# 文章标题

文章正文内容...

EOF

# 2. 一键发布
python -m src.cli.main publish my_article.md

# 3. 查看结果
# - HTML保存在：output/my_article/article.html
# - 草稿保存在：微信公众号后台 → 草稿箱
```

---

## 📋 完整工作流程

### Step 1: 准备文章

**文章格式要求**：
- 必须是Markdown格式（.md文件）
- 必须包含标题（`# 标题` 或 YAML frontmatter）
- 可以使用标准Markdown语法

**可选：在文章中插入图片占位符**

AI会自动优化内容并插入占位符，你也可以手动指定：

```markdown
# 数据图表占位符（会生成精确数据图表）
[[CHART:折线图，横轴为年份（2019-2024），纵轴为占比（%）。显示比特币挖矿中可再生能源占比的变化趋势]]

# 概念插图占位符（会生成AI插图）
[[IMAGE:一个十字路口路标，指向"传统挖矿"和"AI算力"两条不同道路]]
```

---

### Step 2: 执行发布

```bash
# 基本命令
python -m src.cli.main publish article.md

# 指定输出目录
python -m src.cli.main publish article.md --output ./my_output

# 查看详细日志
LOG_LEVEL=DEBUG python -m src.cli.main publish article.md
```

**系统会自动完成**：
1. ✅ 解析Markdown文章
2. ✅ AI生成摘要和封面图提示词
3. ✅ AI优化内容并插入图片占位符
4. ✅ 生成封面图、数据图表、概念插图
5. ✅ 上传所有图片到微信公众号素材库
6. ✅ 嵌入图片URL到HTML
7. ✅ 发布到微信公众号草稿箱

---

### Step 3: 查看结果

**本地文件**：
```bash
ls output/[文章ID]/
# article.html  - 最终HTML文章
# cover_1.png   - 封面图
# chart_1.png   - 数据图表
# illustration_*.png - 概念插图
```

**微信公众号**：
- 登录微信公众号后台
- 进入"草稿箱"
- 查看并编辑草稿
- 确认无误后发布

---

## 🎨 图片占位符系统

### 自动插入（推荐）

不手动添加占位符，让AI自动决定：

```markdown
# 标题

段落内容...

另一个段落...
```

AI会自动识别需要图片的地方并插入：
- `[[CHART:...]]` - 需要数据的地方
- `[[IMAGE:...]]` - 需要视觉说明的地方

### 手动指定（可选）

如果你想在特定位置插入特定类型的图片：

#### 数据图表（CHART）

用于展示精确数值、趋势对比：

```markdown
[[CHART:折线图，横轴为年份（2020-2024），纵轴为用户数量（百万）。显示用户增长趋势]]

[[CHART:柱状图，对比三个产品的销售额（单位：万元）]]

[[CHART:饼图，显示市场份额分布：产品A 40%，产品B 35%，产品C 25%]]
```

**系统行为**：
- 优先使用Matplotlib生成精确图表
- 如果生成失败，降级为AI生成的插图

#### 概念插图（IMAGE）

用于视觉隐喻、场景示意、概念解释：

```markdown
[[IMAGE:一个机器人手与人类手握在一起的场景，象征AI协作]]

[[IMAGE:抽象的双层结构图，底层是波动性可再生能源，上层是储能系统]]
```

**系统行为**：
- 使用豆包AI生成插图
- 自动根据描述生成视觉效果

---

## 🔍 获取真实数据（半自动）

对于数据图表，系统可以查找真实数据：

### 使用Subagent查找数据

在Claude Code中执行：

```
Use the chart-data-researcher subagent to find data for: 折线图，显示比特币挖矿可再生能源占比（2019-2024）
```

Subagent会返回类似这样的数据：

```json
{
  "found": true,
  "chart_data": {
    "type": "line",
    "labels": ["2019", "2020", "2021", "2022", "2023", "2024"],
    "values": [74.1, 41.15, 28.48, 58.9, 59.9, 56.2]
  },
  "source": "比特币矿业委员会 (BMC)"
}
```

### 在文章中使用数据

将获取的数据添加到文章中：

```markdown
# 比特币挖矿能源转型

[[CHART:折线图，横轴为年份（2019-2024），纵轴为占比（%）。数据：2019年74.1%，2020年41.15%，2021年28.48%，2022年58.9%，2023年59.9%，2024年56.2%]]

这个趋势显示了...
```

然后正常发布：

```bash
python -m src.cli.main publish article.md
```

**注意**：
- 如果不提供具体数据，系统会使用默认配置
- 默认配置生成的图表适合测试，但不适合生产环境

---

## 📊 输出说明

### 图片生成规则

1. **封面图**：每篇文章1张，使用AI生成
2. **数据图表**：根据`[[CHART:...]]`占位符数量
3. **概念插图**：根据`[[IMAGE:...]]`占位符数量
4. **降级机制**：图表生成失败时自动转为AI插图

### HTML格式

- 自动适配微信公众号HTML规范
- 图片使用微信CDN URL
- 包含完整的样式和布局

---

## ⚙️ 环境配置

### 必需配置

编辑`.env`文件：

```bash
# DeepSeek AI（文本生成）
DEEPSEEK_API_KEY=your_deepseek_api_key

# 豆包AI（图片生成）
DOUBAO_API_KEY=your_doubao_api_key

# 微信公众号（草稿发布）
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
```

### 可选配置

```bash
# 输出目录
OUTPUT_DIR=./output

# 日志级别
LOG_LEVEL=INFO

# 默认作者
DEFAULT_AUTHOR=默认作者名
```

---

## 🛠️ 常用操作

### 转换Markdown到HTML（不上传）

```bash
python -m src.cli.main convert article.md
```

### 验证HTML是否符合微信规范

```bash
python -m src.cli.main validate article.html
```

### 测试完整流程

```bash
python -m src.cli.main test article.md
```

### 查看生成状态

```bash
# 查看日志
tail -f logs/app.log

# 查看输出的HTML
cat output/[article_id]/article.html
```

---

## 📝 文章示例

### 示例1：简单文章

```markdown
# AI技术的发展

人工智能正在改变我们的生活。

从智能家居到自动驾驶，AI应用无处不在。
```

**处理结果**：
- AI自动生成摘要
- AI生成封面图
- AI识别需要插图的位置并生成
- 发布到草稿箱

### 示例2：带数据图表的文章

```markdown
# 公司年度业绩

2024年我们取得了显著增长。

[[CHART:柱状图，对比2023和2024年四个季度的营收（单位：万元）。Q1: 500→600，Q2: 550→700，Q3: 650→850，Q4: 800→1000]]

这一增长主要得益于...
```

**处理结果**：
- 使用真实数据生成柱状图
- 图表精确显示每个季度的对比
- 其他部分正常处理

### 示例3：复杂的多图片文章

```markdown
# 区块链技术详解

区块链是一种分布式账本技术。

[[CHART:折线图，显示2019-2024年全球区块链市场规模增长（单位：十亿美元）]]

## 核心特性

[[IMAGE:一个区块链网络示意图，多个节点连接形成分布式网络]]

### 去中心化

去中心化是区块链的核心特征。

[[IMAGE:抽象的中心化与去中心化对比图，左侧是单一中心节点，右侧是多个对等节点]]

### 不可篡改

一旦数据写入区块链，就无法被修改。

[[CHART:饼图，显示区块链技术应用领域分布：金融40%，供应链25%，数字身份15%，其他20%]]
```

**处理结果**：
- 1个封面图
- 2个数据图表（折线图、饼图）
- 2个概念插图
- 所有图片自动上传并嵌入
- 完整HTML发布到草稿箱

---

## ⚠️ 注意事项

### 文章要求

1. **必须包含标题**：使用`# 标题`或YAML frontmatter
2. **Markdown格式**：确保文件是.md格式，编码为UTF-8
3. **内容完整**：避免过多占位符或空内容

### 图片占位符

1. **不要过度使用**：每300-500字1-2张图片即可
2. **描述要清晰**：清晰的描述能生成更好的图片
3. **区分类型**：数据用CHART，概念用IMAGE

### 数据准确性

1. **提供真实数据**：在描述中明确数值和单位
2. **使用Subagent验证**：重要数据先用subagent查找
3. **注明数据来源**：在描述中说明"数据来源：xxx"

---

## 🎯 最佳实践

### 工作流程

1. **准备文章** → 编写Markdown格式的完整文章
2. **添加占位符** → 在需要图表/插图的位置添加占位符
3. **验证数据** → 使用subagent验证重要数据的准确性
4. **执行发布** → 运行`python -m src.cli.main publish article.md`
5. **检查结果** → 在微信公众号后台查看草稿
6. **微调发布** → 确认无误后正式发布

### 内容优化

- **标题吸引人**：好的标题能提高阅读率
- **摘要完整**：AI会自动生成，也可以在YAML中手动指定
- **段落清晰**：每段控制在3-5句话
- **图文结合**：文字和图片交替出现，阅读体验更好

---

## 📚 相关文档

- **微信HTML规范**：`docs/wechat_mp_html_css_development_guide.md`
- **Subagent使用**：`docs/CHART_DATA_RESEARCH_GUIDE.md`
- **完整工作流说明**：`docs/CHART_DATA_RESEARCH_SUMMARY.md`
- **Subagent集成状态**：`docs/SUBAGENT_INTEGRATION_STATUS.md`

---

## 💡 常见问题

### Q: AI没有生成图片？
A: 检查`.env`中的API密钥是否正确配置。

### Q: 图表生成失败？
A: 图表生成失败会自动降级为AI插图，这是正常行为。

### Q: 草稿在哪里查看？
A: 登录微信公众号后台 → 草稿箱。

### Q: 能否批量处理多篇文章？
A: 目前需要逐篇处理，可以写简单的shell脚本批量执行。

### Q: 如何修改生成的图片？
A: 图片自动生成，如需修改，可以在微信后台编辑草稿时替换图片。

### Q: 生成的HTML可以直接复制使用吗？
A: 可以，`output/[article_id]/article.html`包含完整的HTML内容。

---

## 🔧 故障排查

### API调用失败

```bash
# 检查配置
cat .env | grep API_KEY

# 测试DeepSeek连接
python -c "from src.ai.deepseek_client import deepseek_client; print(deepseek_client.generate_summary('测试'))"

# 测试豆包连接
python -c "from src.ai.doubao_client import doubao_client; print(doubao_client.generate_illustration('测试', 'test.png'))"
```

### 微信上传失败

```bash
# 测试微信连接
python -c "from src.wechat.api_client import wechat_api_client; print(wechat_api_client.get_access_token())"

# 检查AppID和Secret
cat .env | grep WECHAT
```

### 图片生成失败

查看详细日志：
```bash
LOG_LEVEL=DEBUG python -m src.cli.main publish article.md 2>&1 | grep -E "ERROR|WARN"
```

---

**项目定位**：使用型项目，专注文章发布流程，无需修改代码。

**更新时间**：2025-02-19
**版本**：v2.0 - 使用指南版
