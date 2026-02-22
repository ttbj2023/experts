# 微信公众号自动化推送系统

本文介绍如何使用WeChat Pusher自动化处理微信公众号文章的整个流程。

## 简介

WeChat Pusher是一个基于Python的微信公众号自动化工具，可以将Markdown文章一键转换为符合微信公众号规范的HTML格式，并支持AI自动生成摘要、配图、图表等内容。

## 核心功能

### 1. Markdown转微信HTML

自动将Markdown格式的文章转换为微信公众号支持的HTML格式，严格遵守《微信公众号排版HTML/CSS开发参考指南》的要求：

- **标签白名单过滤**：只使用微信支持的HTML标签
- **样式内联化**：所有CSS样式转换为内联style属性
- **代码块特殊处理**：自动处理空格和换行符，避免缩进丢失
- **图片链接适配**：确保图片符合微信素材库要求

### 2. AI内容生成

集成DeepSeek和豆包AI，实现智能内容生成：

- **文章摘要**：自动生成150-200字的文章摘要
- **图表提示词**：根据文章内容智能生成图表描述
- **配图提示词**：生成封面图和插图的AI绘画提示词

### 3. 数据可视化

自动生成数据图表：

- **柱状图**：适合对比数据
- **折线图**：展示趋势变化
- **饼图**：显示占比分布

所有图表都经过专门设计，符合公众号风格。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制`.env.example`为`.env`并填入API密钥：

```bash
cp .env.example .env
```

编辑`.env`文件，填入以下信息：

- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `DOUBAO_API_KEY`: 豆包API密钥
- `WECHAT_APPID`: 微信公众号AppID
- `WECHAT_SECRET`: 微信公众号AppSecret

### 转换Markdown

```bash
python -m src.cli.main convert article.md
```

### 验证HTML

```bash
python -m src.cli.main validate article.html
```

## 代码示例

这是一个Python代码块的示例：

```python
def hello_wechat():
    """打印欢迎信息"""
    print("Hello, WeChat!")
    return "success"

# 调用函数
result = hello_wechat()
```

## 数据对比

下表展示了使用自动化工具前后的效率对比：

| 指标 | 手动操作 | 自动化工具 | 提升 |
|------|----------|-----------|------|
| 排版时间 | 60分钟 | 5分钟 | 12倍 |
| 配图生成 | 30分钟 | 2分钟 | 15倍 |
| 图表制作 | 45分钟 | 3分钟 | 15倍 |
| 总耗时 | 135分钟 | 10分钟 | 13.5倍 |

## 注意事项

1. **API密钥安全**：不要将`.env`文件提交到版本控制系统
2. **图片资源**：所有图片必须先上传到微信素材库
3. **HTML规范**：严格遵守微信公众号的HTML/CSS规范
4. **测试验证**：推送前务必在微信编辑器中预览效果

## 总结

WeChat Pusher通过自动化流程，将公众号文章制作时间从2小时以上缩短到10分钟以内，大幅提升内容创作效率。

> 💡 **提示**：首次使用建议先运行`test`命令测试完整流程。

---

*本文由WeChat Pusher自动生成*
