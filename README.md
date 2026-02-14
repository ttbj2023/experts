# Assistant Expert Tools

个人助手专家工具集合 - 独立的 Python 包。

## 📦 安装

### 从本地安装（开发模式）

```bash
cd /path/to/assistant-experts
pip install -e .
```

### 从远程仓库安装

```bash
# 从 GitHub 安装
pip install git+https://github.com/your-org/assistant-experts.git

# 安装特定版本
pip install git+https://github.com/your-org/assistant-experts.git@v0.1.0

# 或从 PyPI 安装（发布后）
pip install assistant-experts
```

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

## 🚀 使用

### 方式 1：作为 Python 包导入（推荐）

```python
from assistant_experts import ClaudeDocProcessorExpert
from pathlib import Path

# 初始化专家
expert_root = Path("/path/to/assistant-experts/installation/claude-doc-processor")
expert = ClaudeDocProcessorExpert(expert_root)

# 获取配置
config = expert.get_config()
print(f"专家名称: {config['name']}")
print(f"专家路径: {config['expert_path']}")
print(f"支持格式: {config['supported_formats']}")
```

### 方式 2：通过配置文件

```yaml
# config.yaml
experts:
  use_package_manager: true  # 使用 Python 包管理器

  claude_doc_processor:
    name: "claude-doc-processor"
    enabled: true
    timeout: 600.0
```

## 📦 包结构

```
assistant-experts/
├── pyproject.toml          # 包配置
├── README.md              # 本文件
├── LICENSE               # 许可证
├── .gitignore           # Git 忽略规则
└── src/
    └── assistant_experts/  # 包根目录
        ├── __init__.py      # 包初始化，导出专家类
        └── claude_doc_processor/  # Claude 文档处理专家
            ├── __init__.py
            └── ...
```

## 🔧 包含的专家工具

### claude-doc-processor

文档格式转换和内容增强专家工具。

**功能**：
- 文档格式转换（Markdown ↔ PDF ↔ DOCX ↔ HTML）
- 图片内容识别和分析（基于 zhipu-vision MCP）
- 数据提取和结构化处理
- 文档内容增强和优化

**技术栈**：
- Claude Code CLI（无头模式）
- MinerU 文档解析服务
- zhipu-vision MCP 工具
- Pandoc（文档格式转换）

详细文档：[claude-doc-processor/README.md](./src/assistant_experts/claude_doc_processor/README.md)

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-expert`)
3. 提交更改 (`git commit -m 'feat: 添加 amazing-expert 专家工具'`)
4. 推送到分支 (`git push origin feature/amazing-expert`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🔗 相关链接

- [主仓库](https://github.com/your-org/assistant)
- [Claude Code CLI 文档](https://docs.claude.com/claude-code)
- [zhipu-vision MCP 文档](https://github.com/zhipuai/zhipu-vision-mcp)
