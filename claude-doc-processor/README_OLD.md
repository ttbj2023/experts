# Claude Doc Processor

**版本**: v2.0 (重构版)
**状态**: ✅ 核心重构完成
**更新时间**: 2026-02-17

---

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 使用方法

**PDF转Markdown**
```bash
./convert-pdf.py input.pdf -o output_dir
./convert-pdf.py input.pdf --max-pages 10 --format-with-deepseek
```

**DOCX转Markdown**
```bash
./convert-docx.py input.docx -o output_dir
./convert-docx.py input.docx --glm-api-key YOUR_KEY
```

### 配置

编辑 `config/default.yaml` 或使用环境变量：
```bash
export DEEPSEEK_API_KEY=your_key
./convert-pdf.py input.pdf
```

---

## 📁 项目结构

```
src/
├── core/              # 核心组件
│   ├── glm_client.py
│   ├── deepseek_client.py
│   ├── image_processor.py
│   └── ocr_engine.py
├── converters/        # 转换器
│   ├── base.py
│   ├── pdf_converter.py
│   └── docx_converter.py
├── cli/              # 命令行接口
│   ├── pdf_cmd.py
│   └── docx_cmd.py
└── utils/            # 工具函数
```

---

## 📖 文档

- **重构计划**: `docs/REFACTOR_PLAN.md`
- **配置说明**: `config/default.yaml`
- **旧脚本**: `scripts/` (参考保留)

---

## ✨ 特性

- ✅ 模块化架构（22个组件）
- ✅ 代码复用率85%+
- ✅ YAML配置管理
- ✅ 完整CLI接口
- ✅ 支持5阶段PDF处理
- ✅ 支持4阶段DOCX处理

---

**维护者**: Claude Code
**许可**: MIT License
