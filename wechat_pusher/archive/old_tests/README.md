# WeChat Pusher - 微信公众号AI自动化推送系统

> 将Markdown文章一键转换为符合微信公众号规范的格式，并支持AI自动生成摘要、配图、图表等内容。

## 📖 项目简介

WeChat Pusher是一个完整的Python项目，实现了从Markdown文章到微信公众号草稿箱的全流程自动化处理：

- ✅ **Markdown转微信HTML**：严格遵循微信公众号HTML/CSS规范
- ✅ **AI内容生成**：集成DeepSeek和豆包API
- ✅ **数据可视化**：自动生成图表（柱状图、折线图、饼图）
- ✅ **智能适配**：自动过滤不支持的标签和样式
- ✅ **命令行工具**：简单易用的CLI界面

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
cd wechat_pusher

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入API密钥
# DEEPSEEK_API_KEY=sk-xxx
# DOUBAO_API_KEY=xxx
# WECHAT_APPID=wx123
# WECHAT_SECRET=xxx
```

### 3. 使用

```bash
# 转换Markdown文件
python -m src.cli.main convert examples/sample_article.md

# 验证HTML是否符合微信规范
python -m src.cli.main validate article.html

# 测试完整流程
python -m src.cli.main test examples/sample_article.md
```

## 📚 核心功能

### Markdown转换器

- 支持标准Markdown语法
- 自动提取标题、作者、元数据
- 代码块特殊处理（符合微信规范）
- 表格、列表、引用等完整支持

### HTML构建器

- 基于模板系统
- 多种布局模板（基础排版、卡片布局）
- 完全自定义的样式控制
- 响应式设计

### 微信规范适配器

基于《[微信公众号排版HTML/CSS开发参考指南](docs/wechat_mp_html_css_development_guide.md)》（docs/wechat_mp_html_css_development_guide.md）实现：

- HTML标签白名单过滤
- CSS属性白名单验证
- 代码块空格处理（`\u00A0`替换）
- 图片、链接特殊处理

### AI内容生成

#### DeepSeek集成

- 📝 生成文章摘要
- 📊 生成图表提示词和数据
- 🎨 生成配图提示词
- ✏️ 内容优化润色

#### 豆包集成

- 🖼️ 生成封面图（16:9）
- 🖼️ 生成插图（1:1或自定义比例）
- 💾 图片下载和缓存

### 图表生成器

使用Matplotlib生成专业图表：

- 📊 柱状图（Bar Chart）
- 📈 折线图（Line Chart）
- 🥧 饼图（Pie Chart）
- 🎨 符合公众号风格的配色

## 📁 项目结构

```
wechat_pusher/
├── src/                        # 源代码
│   ├── converter/              # 转换模块
│   │   ├── markdown_parser.py  # Markdown解析器
│   │   ├── html_builder.py     # HTML构建器
│   │   └── wechat_adapter.py   # 微信规范适配器
│   ├── ai/                     # AI模块
│   │   ├── deepseek_client.py  # DeepSeek客户端
│   │   └── doubao_client.py    # 豆包客户端
│   ├── chart/                  # 图表模块
│   │   └── chart_generator.py  # 图表生成器
│   ├── wechat/                 # 微信API（待实现）
│   ├── utils/                  # 工具模块
│   │   ├── config.py           # 配置管理
│   │   └── logger.py           # 日志工具
│   └── cli/                    # 命令行工具
│       └── main.py             # CLI入口
├── templates/                  # HTML模板
│   ├── basic.html              # 基础模板
│   └── card.html               # 卡片模板
├── examples/                   # 示例文件
│   └── sample_article.md       # 示例文章
├── docs/                       # 文档
│   └── wechat_mp_html_css_development_guide.md
├── tests/                      # 测试用例
├── output/                     # 输出目录
│   ├── html/                   # 生成的HTML
│   ├── images/                 # AI生成的图片
│   └── charts/                 # 生成的图表
├── requirements.txt            # 依赖清单
├── .env.example                # 环境变量模板
└── README.md                   # 本文档
```

## 🛠️ CLI命令

### convert - 转换Markdown

```bash
# 基础用法
python -m src.cli.main convert article.md

# 指定输出文件
python -m src.cli.main convert article.md -o output.html

# 使用卡片模板
python -m src.cli.main convert article.md -t card
```

### validate - 验证HTML

```bash
python -m src.cli.main validate article.html
```

### test - 测试流程

```bash
python -m src.cli.main test article.md
```

## ⚙️ 配置说明

### 环境变量

所有配置通过`.env`文件管理：

```bash
# DeepSeek AI
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 豆包AI
DOUBAO_API_KEY=xxx
DOUBAO_MODEL=doubao-v3

# 微信公众号
WECHAT_APPID=wx123
WECHAT_SECRET=xxx

# 应用配置
OUTPUT_DIR=./output
LOG_LEVEL=INFO
LOG_COLOR=true
```

详见[`.env.example`](.env.example)文件。

## 📖 开发指南

### 添加新的HTML模板

1. 在`templates/`目录创建新的HTML文件
2. 使用`$title`、`$content`、`$author`等变量
3. 通过`-t`参数指定模板名

### 扩展图表类型

在`src/chart/chart_generator.py`中添加新的图表生成方法。

### 自定义微信适配规则

修改`src/converter/wechat_adapter.py`中的白名单和过滤规则。

## 🔄 工作流程

```
Markdown文件
    ↓
[MarkdownParser] 解析内容
    ↓
[HTMLBuilder] 构建HTML
    ↓
[WeChatAdapter] 适配规范
    ↓
[DeepSeekClient] 生成AI内容（可选）
    ↓
[ChartGenerator] 生成图表（可选）
    ↓
[DoubaoClient] 生成图片（可选）
    ↓
[微信API] 上传素材、创建草稿（待实现）
    ↓
微信公众号草稿箱
```

## 📝 待实现功能

- [ ] 微信公众号API完整集成
- [ ] 素材自动上传
- [ ] 草稿箱自动创建
- [ ] 批量处理功能
- [ ] 完整单元测试
- [ ] 配置热重载
- [ ] Web界面（可选）

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Python-Markdown](https://python-markdown.github.io/) - Markdown解析
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML处理
- [Matplotlib](https://matplotlib.org/) - 图表生成
- [Click](https://click.palletsprojects.com/) - CLI框架

---

**Made with ❤️ by Claude Code**
