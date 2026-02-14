# Claude文档处理专家子项目

这是Personal Agent Assistant项目的文档处理专家子项目，作为独立的Git Submodule运行。

## 项目概述

本子项目是专业的文档处理专家，通过Claude Code CLI无头模式提供以下功能：

- **格式转换**: PDF ↔ DOCX ↔ Markdown ↔ HTML ↔ TXT ↔ EPUB
- **内容提取**: 从复杂格式（PDF/DOCX）提取文本、表格、图片
- **内容优化**: 重新组织内容、美化格式、提取关键信息
- **图片处理**: 自动生成图片描述并嵌入文档

## 目录结构

```
claude-doc-processor/
├── CLAUDE.md                   # 子项目核心指令（根目录）
├── .claude/
│   └── settings.json          # MCP配置（zhipu-vision等）
├── scripts/
│   ├── call_mineru.sh         # MinerU服务调用脚本
│   └── validate_output.sh     # 输出文件验证脚本
└── README.md                  # 本文件
```

## 核心功能

### 1. 格式转换

支持各种文档格式之间的双向转换：

- PDF → DOCX/Markdown/HTML/TXT
- DOCX → PDF/Markdown/HTML
- Markdown → PDF/DOCX/HTML
- HTML → PDF/Markdown/DOCX

### 2. 内容提取

从复杂格式文档中提取结构化内容：

- 提取文本内容并保留层级结构
- 提取表格并保留数据完整性
- 提取图片并生成描述
- 识别和提取公式、图表

### 3. 内容优化

根据用户需求优化文档内容：

- 重新组织章节结构
- 美化格式和排版
- 提取关键信息生成摘要
- 修正格式错误和不一致

### 4. 图片处理

自动处理文档中的图片：

- 使用zhipu-vision MCP生成图片描述
- 将图片URL和描述嵌入Markdown
- 优化图片在目标格式中的显示效果

## 依赖服务

### MinerU服务

**功能**: 专业文档解析服务
**API地址**: `http://localhost:8177`（当前配置）
**API端点**: `/file_parse`
**特性**:
- PDF/DOCX转Markdown，保留格式
- 表格识别和提取
- 公式识别
- 多语言支持

**环境变量**:
```bash
export MINERU_API_URL="http://localhost:8177"
export OUTPUT_DIR="/tmp/mineru_output"
export LANG_LIST="ch"  # ch: 中文/英文, en: 英文
export BACKEND="pipeline"  # pipeline: 通用, hybrid-auto-engine: 高精度
```

**参数说明**:
- `files`: 文件数组（支持PDF、图片）
- `output_dir`: 输出目录
- `lang_list`: 语言列表
- `backend`: 解析后端类型
- `parse_method`: 解析方法（auto/txt/ocr）
- `formula_enable`: 启用公式解析
- `table_enable`: 启用表格解析

### zhipu-vision MCP

**功能**: 图片描述生成服务
**配置**: 在`.claude/settings.json`中启用
**特性**:
- 自动识别图片内容
- 生成简洁准确的中文描述
- 支持多种图片格式

### Pandoc工具

**功能**: 通用文档转换工具
**安装**: `apt-get install pandoc`（Linux）或 `brew install pandoc`（Mac）
**支持格式**: 40+种文档格式

## 使用方式

### 作为Git Submodule

本子项目作为主项目的Git Submodule运行：

```bash
# 在主项目根目录
git submodule add https://github.com/your-org/claude-doc-processor.git \
  src/tools/experts/claude-doc-processor
```

### 环境变量配置

```bash
# MinerU服务地址（可选，默认http://localhost:8001）
export MINERU_API_URL="http://localhost:8001"

# 输入文件路径（由主项目自动传递）
export INPUT_FILE="/path/to/input.pdf"

# 输出文件路径（由主项目自动传递）
export OUTPUT_FILE="/path/to/output.docx"
```

### 通过主项目调用

主项目通过`document_processing_expert`工具调用本子项目：

```python
from src.tools.internal.document_processing_expert_tool import DocumentProcessingExpertTool

tool = DocumentProcessingExpertTool(
    user_id="alice",
    thread_id="main"
)

result = await tool._arun(
    file_path="/path/to/document.pdf",
    instructions="转换为Word文档并优化格式",
    output_format="docx"
)
```

## 辅助脚本

### call_mineru.sh

调用MinerU服务将文档转换为Markdown。

**使用方法**:
```bash
./scripts/call_mineru.sh /path/to/document.pdf
```

**输出**: JSON文件，包含markdown内容和图片信息

### validate_output.sh

验证生成的输出文件是否有效。

**使用方法**:
```bash
./scripts/validate_output.sh /path/to/output.pdf
```

**验证内容**:
- 文件存在性
- 文件大小（非空）
- 文件格式有效性（根据扩展名）

## 配置文件

### CLAUDE.md

子项目的核心指令文档，定义：
- 角色定位和能力
- 处理流程和策略
- 可用资源和工具
- 工作原则和质量标准

### .claude/settings.json

Claude Code CLI的配置文件，包含：
- MCP服务配置（zhipu-vision）
- 工具权限控制（Read、Edit、Bash）
- 安全策略设置

## 开发和测试

### 本地测试

```bash
# 设置环境变量
export INPUT_FILE="test.pdf"
export OUTPUT_FILE="output.docx"

# 调用Claude Code CLI
claude -p "处理文档并转换为Word格式" --print
```

### 脚本测试

```bash
# 测试MinerU调用
./scripts/call_mineru.sh test.pdf

# 测试输出验证
./scripts/validate_output.sh output.docx
```

## 性能指标

- **简单格式转换**（TXT/MD）: 5-15秒
- **复杂格式处理**（PDF/DOCX）: 30-120秒
- **大文件处理**（>50MB）: 2-5分钟
- **图片描述生成**: 1-3秒/张

## 故障排查

### MinerU服务不可用

**问题**: `curl: (7) Failed to connect to localhost port 8001`

**解决**:
1. 检查MinerU服务是否运行：`curl http://localhost:8001/health`
2. 启动MinerU服务：`mineru-api --host 0.0.0.0 --port 8001`
3. 验证服务状态：`ps aux | grep mineru`

### Pandoc命令未找到

**问题**: `pandoc: command not found`

**解决**:
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# 验证安装
pandoc --version
```

### 图片描述生成失败

**问题**: zhipu-vision MCP调用失败

**解决**:
1. 检查`.claude/settings.json`中MCP配置
2. 验证zhipu-vision服务可用性
3. 检查API密钥配置

## 版本历史

### v1.0.0 (2026-02-14)
- 初始版本发布
- 支持PDF/DOCX/Markdown/HTML/TXT格式
- 集成MinerU和zhipu-vision
- 提供辅助脚本

## 贡献指南

本子项目作为独立的Git仓库管理：

1. Fork本仓库
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交变更：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建Pull Request

## 许可证

本子项目遵循主项目的许可协议。

## 联系方式

- **项目主页**: https://github.com/your-org/claude-doc-processor
- **问题反馈**: https://github.com/your-org/claude-doc-processor/issues
- **维护团队**: Claude Code Subproject Team

---

**最后更新**: 2026-02-14
**项目版本**: 1.0.0
