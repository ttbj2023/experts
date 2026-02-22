# WeChat Pusher - 微信公众号AI自动化推送系统

> 将Markdown文章自动转换为微信公众号格式，AI生成配图和图表，一键发布到草稿箱

## ✨ 核心特性

### 🤖 AI增强
- **DeepSeek AI**：自动生成摘要、优化内容、生成配图提示词
- **豆包 AI**：生成封面图和概念插图
- **智能占位符**：AI自动识别需要图片的位置并插入占位符
- **Gemini + Google Search**：自动查找真实数据生成精确图表

### 📊 智能图表系统
- **数据图表（CHART）**：使用Matplotlib生成精确数据图表
- **概念插图（IMAGE）**：AI生成视觉化说明图片

### 🎨 微信公众号优化
- **完美适配**：自动转换为微信公众号HTML规范
- **跨平台字体**：支持iOS/Android/Windows不同平台
- **数学公式**：LaTeX公式自动转换为Unicode数学符号
- **代码高亮**：优化的代码块样式

### 🚀 一键发布
- **自动上传**：图片自动上传到微信公众号素材库
- **草稿箱**：直接发布到草稿箱，随时编辑
- **完整流程**：从Markdown到微信草稿，全自动完成

---

## 🎯 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env.example`到`.env`并配置：

```bash
# DeepSeek AI（文本生成）
DEEPSEEK_API_KEY=your_deepseek_api_key

# 豆包AI（图片生成）
DOUBAO_API_KEY=your_doubao_api_key

# 微信公众号（草稿发布）
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
```

详细配置见：[docs/QUICK_START.md](docs/QUICK_START.md)

### 3. 一键发布

```bash
# 发布文章到微信公众号草稿箱
python -m src.cli.main publish article.md

# 查看结果
# - HTML保存在：output/[文章ID]/article.html
# - 草稿保存在：微信公众号后台 → 草稿箱
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

## 📚 使用指南

### 基础使用

```bash
# 发布文章
python -m src.cli.main publish article.md

# 指定作者
python -m src.cli.main publish article.md --author "张三"

# 转换为HTML（不上传）
python -m src.cli.main convert article.md

# 验证HTML
python -m src.cli.main validate article.html
```

### 系统自动完成

1. **文章优化**：DeepSeek AI优化内容，适配微信公众号阅读习惯
2. **智能配图**：自动识别需要图片的位置，生成数据图表和概念插图
3. **数据查找**：使用Gemini + Google Search自动查找真实数据
4. **图片生成**：豆包AI生成封面图和插图
5. **自动发布**：上传素材到微信，创建草稿

---

## 📖 文档

### 核心文档
- **[CLAUDE.md](CLAUDE.md)** - 完整使用指南（推荐新手阅读）
- **[docs/CONVERTER_USAGE.md](docs/CONVERTER_USAGE.md)** - Markdown转换器详细说明

### 配置指南
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - 微信API快速配置
- **[docs/WECHAT_API_SETUP.md](docs/WECHAT_API_SETUP.md)** - 微信API详细配置

### 高级功能
- **[docs/AUTO_PUBLISHING_GUIDE.md](docs/AUTO_PUBLISHING_GUIDE.md)** - 自动发布完整流程
- **[docs/CHART_DATA_RESEARCH_GUIDE.md](docs/CHART_DATA_RESEARCH_GUIDE.md)** - 图表数据查找指南

### 参考文档
- **[docs/wechat_mp_html_css_development_guide.md](docs/wechat_mp_html_css_development_guide.md)** - 微信HTML/CSS开发规范

---

## 🎨 模板系统

项目使用**demis_hassabis**模板作为默认模板：

- **专业风格**：科技访谈类文章的专业排版
- **开篇引用框**：灰色背景突出文章摘要
- **视觉优化**：黄色阴影标题、精心调校的字体和间距
- **移动端适配**：完美适配微信公众号

**模板切换**：

可以在`.env`中配置：

```bash
# 使用默认模板（demis_hassabis）
DEFAULT_TEMPLATE=demis_hassabis
```

> **注意**：其他模板（basic、card）已归档到`archive/old_templates/`目录。

---

## 📁 项目结构

```
wechat_pusher/
├── src/
│   ├── ai/                  # AI客户端（DeepSeek、豆包）
│   ├── chart/               # 图表生成器
│   ├── cli/                 # 命令行工具
│   ├── converter/           # Markdown转换器
│   ├── services/            # 图表数据查找服务
│   ├── utils/               # 工具类（配置、日志）
│   ├── wechat/              # 微信API客户端
│   └── workflow/            # 发布工作流
├── templates/               # HTML模板
│   └── basic.html          # 默认模板
├── docs/                    # 文档
├── examples/                # 示例文章
├── archive/                 # 归档文件
├── CLAUDE.md               # 使用指南
├── CHANGELOG.md            # 更新日志
└── README.md               # 本文件
```

---

## ⚙️ 环境要求

- **Python**: 3.12+
- **操作系统**: Linux/macOS/Windows
- **网络**: 需要访问以下API
  - DeepSeek API
  - 豆包 API
  - 微信公众号API

---

## 🔄 更新日志

查看最新更新：[CHANGELOG.md](CHANGELOG.md)

### v2.1 (2025-02-20)
- ✅ 简化模板系统，使用优化的basic模板
- ✅ 修复ArticlePublisher未使用DEFAULT_TEMPLATE配置的问题
- ✅ 归档旧模板，清理项目结构
- ✅ 添加主README.md和CLAUDE.md

---

## 🆘 常见问题

### Q: AI没有生成图片？
A: 检查`.env`中的API密钥是否正确配置。

### Q: 图表生成失败？
A: 如果找不到合适的数据，图表不会生成，这是正常行为。文章仍然会正常发布。

### Q: 草稿在哪里查看？
A: 登录微信公众号后台 → 草稿箱。

### Q: 如何修改生成的图片？
A: 图片自动生成，如需修改，可以在微信后台编辑草稿时替换图片。

### Q: 能否批量处理多篇文章？
A: 目前需要逐篇处理，可以写简单的shell脚本批量执行。

更多问题见：[CLAUDE.md#常见问题](CLAUDE.md)

---

## 📝 许可证

本项目为私有项目，仅供授权用户使用。

---

## 🤝 贡献

欢迎提交Issue和Pull Request。

---

**项目定位**：使用型项目，专注文章发布流程，无需修改代码。

**最后更新**：2025-02-20
**当前版本**：v2.1
