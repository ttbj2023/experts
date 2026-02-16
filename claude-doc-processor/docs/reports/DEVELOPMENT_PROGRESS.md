# PDF→Word兼容HTML「画框→识别→填空」开发进度报告

**更新时间**: 2026-02-15
**项目状态**: 阶段一完成，阶段二进行中
**完成度**: 约 40%

---

## 📊 总体进度

### ✅ 已完成（阶段一 + 模块1）

#### 阶段一：基础规范与模板定义
1. **✅ 项目目录结构**
   - 创建了 `config/`, `templates/`, `src/`, `tests/` 目录
   - 符合模块化设计原则

2. **✅ 元素类型映射表** (`config/element_mapping.yaml`)
   - 定义了11类元素的完整映射（标题h1-h6、段落、列表、公式、表格、图片、页眉页脚）
   - 包含元素分组、特殊处理规则、验证规则
   - 提供了模型Prompt映射

3. **✅ 数据流转协议** (`config/data_protocol.yaml`)
   - 定义了三阶段的JSON数据格式
   - 画框输出：`page_layout.json`（元素框清单）
   - 识别输出：`page_content.json`（填充内容）
   - 填空输出：`final.html`（完整HTML）
   - 包含错误处理、批处理、质量评估协议

4. **✅ HTML模板库** (`templates/word_html_templates.yaml`)
   - 全局HTML骨架（严格HTML4.01 + DOCTYPE）
   - 全局CSS样式（仅CSS2.1子集，100% Word兼容）
   - 11类元素的Jinja2模板
   - 合规性检查规则（禁用标签/属性）
   - 测试用例

#### 阶段二：核心模块开发
5. **✅ 工具函数模块** (`src/utils.py`)
   - PDF转高清图片（PyMuPDF，200 DPI）
   - 图片压缩优化（支持多级压缩）
   - base64编码/解码
   - 视觉模型API调用（OpenAI格式）
   - JSON数据处理
   - 边界框验证、IoU计算、重叠检测

6. **✅ 画框模块** (`src/layout_analyzer.py`)
   - `LayoutAnalyzer`类实现
   - 专用版面分析Prompt（识别11类元素、双栏布局、阅读顺序）
   - 视觉模型API集成
   - JSON响应解析
   - 版面分析验证（重叠检测、字段完整性）
   - 单页/多页PDF处理
   - 调试图片和原始响应保存

---

## 🚧 进行中

### 阶段二剩余模块（待开发）

#### 模块2：识别模块 (`src/content_extractor.py`)
**优先级**: P0（核心功能）

**计划实现**:
- `ContentExtractor`类
- 元素裁剪（根据bbox从页面截图裁剪小图）
- 分类型Prompt设计：
  - 文本类Prompt（标题/段落/列表）
  - 公式类Prompt（LaTeX转换）
  - 表格类Prompt（结构化数据提取）
  - 图片类Prompt（图片描述 + base64提取）
- 内容组装（公式占位符替换、列表嵌套处理）
- 质量指标记录

**预计开发时间**: 1-2天

#### 模块3：填空模块 (`src/html_generator.py`)
**优先级**: P0（核心功能）

**计划实现**:
- `HTMLGenerator`类
- 模板加载（Jinja2）
- 元素级模板渲染
- 双栏布局组装（跨栏元素 vs 栏内元素）
- 全局HTML组装
- 合规性自检（禁用标签/属性检测）
- HTML文件保存

**预计开发时间**: 1-2天

---

## 📅 待开始（阶段三-四）

### 阶段三：集成与测试（预计2-3天）

#### 任务1：主流程集成 (`src/main.py`)
- 三阶段流程串联
- 错误处理和重试
- 进度显示
- 批处理支持

#### 任务2：CLI工具 (`cli.py`)
- 命令行参数解析
- 基础功能：
  ```bash
  python cli.py input.pdf output.html
  ```
- 高级选项（模型选择、页码范围、DPI设置）

#### 任务3：测试
- 单元测试（`tests/`目录）
- 真实文档测试（简单/数学教材/复杂排版）
- Word兼容性验收测试

### 阶段四：优化与文档（预计1-2天）

#### 任务1：性能优化
- 批量API调用并发
- 图片压缩策略优化
- 缓存机制

#### 任务2：文档编写
- `README.md`: 快速开始、安装说明、使用示例
- `ARCHITECTURE.md`: 系统架构设计
- `API.md`: 模块接口文档
- `PROMPTS.md`: Prompt设计说明

---

## 📁 当前项目结构

```
claude-doc-processor/
├── config/
│   ├── element_mapping.yaml      ✅ 完成
│   └── data_protocol.yaml        ✅ 完成
├── templates/
│   └── word_html_templates.yaml  ✅ 完成
├── src/
│   ├── utils.py                  ✅ 完成
│   ├── layout_analyzer.py        ✅ 完成
│   ├── content_extractor.py      ⏳ 待开发
│   ├── html_generator.py         ⏳ 待开发
│   └── main.py                   ⏳ 待开发
├── cli.py                         ⏳ 待开发
├── tests/                         ⏳ 待编写
├── docs/                          ⏳ 待编写
└── requirements_new.txt          ⏳ 待整理
```

---

## 🎯 下一步行动计划

### 立即开始（建议）
1. **开发识别模块** (`content_extractor.py`)
   - 实现元素裁剪功能
   - 设计分类型Prompt
   - 实现批量API调用
   - 完成内容组装逻辑

2. **开发填空模块** (`html_generator.py`)
   - 实现模板加载和渲染
   - 实现双栏布局组装
   - 实现合规性自检

3. **集成主流程** (`main.py`)
   - 串联三阶段流程
   - 添加错误处理
   - 实现单页处理功能

### 可选（后续优化）
- CLI工具开发
- 单元测试
- 性能优化
- 文档完善

---

## 💡 技术亮点

### 已实现
1. **严格遵循Word兼容规范**
   - HTML4.01 + CSS2.1子集
   - 禁用HTML5标签和CSS3属性
   - 公式使用`<script type="math/tex">`标签
   - 图片base64内嵌

2. **模块化设计**
   - 清晰的模块边界
   - JSON数据协议解耦
   - 可独立测试和优化

3. **视觉模型集成**
   - 支持OpenAI API格式
   - 图片压缩优化
   - 重试机制

4. **质量保证**
   - 边界框验证
   - 重叠检测
   - 阅读顺序校验
   - 合规性自检

### 待实现
- 11类元素的完整支持
- LaTeX公式高质量提取
- 表格结构化识别
- 双栏布局智能处理

---

## ⚠️ 当前限制

1. **依赖外部视觉模型**
   - 需要稳定的GLM-4.6V或Qwen3VL服务
   - API调用速度影响处理效率

2. **未优化性能**
   - 当前为顺序处理
   - 未实现并发和缓存

3. **测试不完整**
   - 仅完成核心代码
   - 未进行真实场景测试

---

## 📊 开发进度统计

| 模块 | 状态 | 完成度 | 预计剩余时间 |
|------|------|--------|--------------|
| 阶段一：配置与模板 | ✅ 完成 | 100% | 0天 |
| 模块1：画框 | ✅ 完成 | 100% | 0天 |
| 模块2：识别 | ⏳ 进行中 | 0% | 1-2天 |
| 模块3：填空 | ⏳ 待开始 | 0% | 1-2天 |
| 阶段三：集成测试 | ⏳ 待开始 | 0% | 2-3天 |
| 阶段四：优化文档 | ⏳ 待开始 | 0% | 1-2天 |
| **总计** | **进行中** | **~40%** | **5-9天** |

---

## 🚀 使用示例（开发完成后）

```bash
# 基础用法
python cli.py input.pdf output.html

# 高级选项
python cli.py input.pdf output.html \
  --model qwen3vl \
  --start-page 1 \
  --end-page 10 \
  --dpi 200

# 批量处理
python cli.py batch_process input_dir/ output_dir/
```

---

**维护者**: Claude Code Subproject Team
**最后更新**: 2026-02-15
