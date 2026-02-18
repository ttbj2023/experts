# Processors 目录

**状态**: 预留扩展目录
**创建时间**: 2026-02-18

---

## 📁 目录用途

此目录预留用于存放**专用处理器模块**。

---

## 🎯 预期用途

虽然当前v4.0架构中所有处理逻辑已集成在：
- `src/converters/` - 转换器
- `src/core/` - 核心引擎
- `src/utils/` - 工具函数

但未来可能需要独立的处理器，例如：

### 可能的处理器类型
1. **文档预处理**
   - 图片压缩处理器
   - 格式清理处理器
   - 编码转换处理器

2. **内容后处理**
   - 公式验证处理器
   - 表格格式化处理器
   - 引用规范化处理器

3. **特殊格式处理**
   - EPUB处理器
   - PowerPoint处理器
   - Excel处理器

---

## 💡 设计原则

如果将来需要添加处理器，请遵循：

### 1. 继承基类
```python
from src.converters.base import BaseConverter

class MyProcessor(BaseConverter):
    def process(self, input_path, output_path):
        # 处理逻辑
        pass
```

### 2. 统一接口
```python
# 输入：文件路径
# 输出：处理结果或新文件路径
```

### 3. 可配置化
使用 `config/default.yaml` 添加配置项

---

## 📖 参考

- **转换器**: `../converters/`
- **核心引擎**: `../core/`
- **工具函数**: `../utils/`

---

**维护者**: Claude Code
**最后更新**: 2026-02-18
