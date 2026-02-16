# Claude Doc Processor - 项目文档

**更新时间**: 2026-02-17
**状态**: ✅ 核心重构完成

---

## 📚 文档列表

### 核心文档
1. **重构计划** - `docs/REFACTOR_PLAN.md`
   - 完整的重构计划和执行记录
   - 架构设计说明
   - 进度跟踪

2. **配置文件** - `config/default.yaml`
   - 模型配置（GLM, DeepSeek）
   - 处理配置（PDF, DOCX）
   - OCR提示词模板

3. **使用文档** - `README.md`
   - 快速开始指南
   - CLI使用说明
   - 配置方法

### 旧版文档（已归档）
- `archive/legacy_docs/README.md.v1`
- `archive/legacy_docs/CLAUDE.md.v1`

---

## 🏗️ 架构文档

### 项目结构
```
src/
├── core/          # 核心组件（1450行）
│   ├── glm_client.py
│   ├── deepseek_client.py
│   ├── image_processor.py
│   └── ocr_engine.py
├── converters/    # 转换器（1150行）
│   ├── base.py
│   ├── pdf_converter.py
│   └── docx_converter.py
├── cli/          # CLI接口（351行）
│   ├── pdf_cmd.py
│   └── docx_cmd.py
└── utils/       # 工具函数（1405行）
    └── [8个工具模块]
```

### 处理流程

**PDF转换（5阶段）**:
1. GLM OCR + 占位符生成
2. DeepSeek排版优化（可选）
3. OpenCV图片提取
4. GLM图片描述
5. DeepSeek语义匹配
6. 占位符替换

**DOCX转换（4阶段）**:
1. DOCX图片提取 + LibreOffice转换 + GLM识别
2. GLM图片描述
3. DeepSeek语义匹配（全局上下文）
4. 智能占位符替换

---

## 📊 重构成果

| 指标 | 重构前 | 重构后 | 改善 |
|------|--------|--------|------|
| 代码重复率 | ~30% | <10% | ↓ 67% |
| 模块数量 | 2个脚本 | 22个模块 | 清晰架构 |
| 配置管理 | 硬编码 | YAML配置 | 灵活 |
| CLI接口 | 无 | 完整 | 可用 |

---

## 🔧 开发指南

### 添加新格式支持
1. 继承 `BaseConverter`
2. 使用core组件
3. 实现 `convert()` 方法
4. 创建CLI命令

### 扩展core组件
- GLMClient: 添加新的API调用方法
- DeepSeekClient: 添加新的处理模式
- ImageProcessor: 支持新的提取方式
- OCREngine: 添加新的清理规则

---

**维护者**: Claude Code

