# WeChat Pusher - 快速开始指南

## 🎉 项目已成功创建！

恭喜！您的微信公众号自动化推送系统基础框架已经搭建完成。

## ✅ 已完成的功能

### Phase 1: 基础架构 ✅
- [x] 项目目录结构
- [x] 依赖管理（requirements.txt）
- [x] 环境变量配置（.env.example）
- [x] 配置管理模块（config.py）
- [x] 日志工具（logger.py）

### Phase 2: 转换器模块 ✅
- [x] Markdown解析器（markdown_parser.py）
- [x] HTML构建器（html_builder.py）
- [x] 微信规范适配器（wechat_adapter.py）
- [x] HTML模板（basic.html, card.html）

### Phase 3: AI集成 ✅
- [x] DeepSeek客户端（deepseek_client.py）
- [x] 豆包客户端（doubao_client.py）

### Phase 4: 图表生成 ✅
- [x] 图表生成器（chart_generator.py）
- [x] 支持柱状图、折线图、饼图

### Phase 5: CLI工具 ✅
- [x] 命令行界面（main.py）
- [x] convert命令（MD转HTML）
- [x] validate命令（验证HTML）
- [x] test命令（完整测试）

### 文档和示例 ✅
- [x] README.md（项目说明）
- [x] 示例Markdown文件
- [x] 微信开发指南（docs/）
- [x] setup.py（安装配置）
- [x] .gitignore（版本控制）

## 🚀 立即开始使用

### 1. 安装依赖

```bash
# 激活虚拟环境（如果还没激活）
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

如果想测试完整的AI功能，需要配置API密钥：

```bash
# 复制配置模板
cp .env.example .env

# 编辑.env文件，填入：
# - DEEPSEEK_API_KEY
# - DOUBAO_API_KEY
# - WECHAT_APPID
# - WECHAT_SECRET
```

**注意**：如果不配置这些，转换功能仍然可以正常使用，只是AI功能不可用。

### 3. 测试转换功能

```bash
# 测试完整流程
python -m src.cli.main test examples/sample_article.md
```

### 4. 转换自己的文章

```bash
# 转换Markdown文件
python -m src.cli.main convert your_article.md

# 使用卡片模板
python -m src.cli.main convert your_article.md -t card

# 指定输出路径
python -m src.cli.main convert your_article.md -o output.html
```

### 5. 验证HTML

```bash
# 验证生成的HTML是否符合微信规范
python -m src.cli.main validate your_article.html
```

## 📋 下一步开发

以下是尚未完成的功能，可以继续开发：

### Phase 5: 微信公众号API集成（待实现）
- [ ] API认证管理（auth_manager.py）
- [ ] 素材上传（media_uploader.py）
- [ ] 草稿箱管理（draft_manager.py）
- [ ] 完整的微信API客户端（api_client.py）

### 高级功能
- [ ] 批量处理目录
- [ ] 自动调用AI生成内容
- [ ] 自动生成图表
- [ ] 自动生成配图
- [ ] 一键推送到草稿箱

### 测试和优化
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 错误处理增强

## 📖 使用示例

### 示例1：基础转换

```bash
python -m src.cli.main convert examples/sample_article.md
```

输出：
```
✅ 转换成功！
📄 HTML已保存到: examples/sample_article.html

📊 文章信息:
   标题: 微信公众号自动化推送系统
   字数: 1234
   图片: 0张
   代码块: 2个
```

### 示例2：使用卡片模板

```bash
python -m src.cli.main convert article.md -t card
```

### 示例3：验证HTML

```bash
python -m src.cli.main validate article.html
```

输出：
```
✅ HTML验证通过！符合微信公众号规范
```

或

```
❌ HTML验证失败，发现 2 个问题：

   1. 发现禁用标签: <script>
   2. 发现禁用的CSS属性: position
```

## 🔧 自定义配置

### 修改日志级别

编辑`.env`文件：

```bash
LOG_LEVEL=DEBUG  # 输出详细日志
# 或
LOG_LEVEL=ERROR  # 只输出错误信息
```

### 自定义HTML模板

1. 在`templates/`目录创建新模板文件
2. 使用变量：`$title`, `$content`, `$author`, `$summary`
3. 使用时指定模板名：`-t your_template`

## 🐛 故障排除

### 问题1：模块导入错误

```bash
# 确保在项目根目录
cd wechat_pusher

# 确保虚拟环境已激活
source .venv/bin/activate  # Linux/Mac
```

### 问题2：依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：字体问题（图表生成）

```bash
# Linux系统可能需要安装中文字体
sudo apt-get install fonts-wqy-microhei
```

## 📚 相关文档

- [README.md](README.md) - 完整项目说明
- [微信开发指南](docs/wechat_mp_html_css_development_guide.md) - 微信HTML/CSS规范
- [.env.example](.env.example) - 配置说明

## 🎯 核心模块说明

### 转换器模块（src/converter/）
- **markdown_parser.py**: 将Markdown文件解析为结构化数据
- **html_builder.py**: 根据模板构建HTML
- **wechat_adapter.py**: 确保HTML符合微信规范（核心）

### AI模块（src/ai/）
- **deepseek_client.py**: 文本生成（摘要、提示词等）
- **doubao_client.py**: 图片生成

### 图表模块（src/chart/）
- **chart_generator.py**: 生成数据可视化图表

### 工具模块（src/utils/）
- **config.py**: 配置管理
- **logger.py**: 日志记录

## 💡 开发提示

### 添加新的图表类型

编辑`src/chart/chart_generator.py`，添加新方法：

```python
def _generate_scatter_chart(self, data: Dict, save_path: str) -> str:
    """生成散点图"""
    # 实现代码
    pass
```

### 扩展微信适配规则

编辑`src/converter/wechat_adapter.py`，修改白名单：

```python
ALLOWED_TAGS = {
    # 添加新的支持标签
    "your_tag",
}
```

## 🎊 总结

您的微信公众号自动化推送系统已经完成了核心功能的开发！

现在可以：
1. ✅ 将Markdown转换为微信HTML
2. ✅ 验证HTML是否符合规范
3. ✅ 使用两种不同的HTML模板
4. ✅ 集成AI功能（需要配置API密钥）
5. ✅ 生成数据图表

下一步可以根据实际需求继续开发微信API集成部分，实现从Markdown到草稿箱的全自动化流程！

---

**Happy Coding! 🚀**
