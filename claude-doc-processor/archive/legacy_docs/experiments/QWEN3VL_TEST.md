# Qwen3-VL-8B PDF识别测试指南

## 📦 测试环境

### 已创建的文件
1. **主脚本**：`scripts/process_pdf_with_qwen3vl.py`
   - 基于GLM-4.6V版本改造
   - 适配Ollama API
   - 使用64K上下文（与GLM-4.6V一致）

2. **测试脚本**：`scripts/test_qwen3vl.sh`
   - 一键测试脚本
   - 自动检查Ollama服务
   - 测试前3页默认

3. **配置文件**：`scripts/config_qwen3vl.sh`
   - 环境变量配置
   - 可选加载

---

## 🚀 快速开始

### 前提条件
```bash
# 1. 确认Ollama服务运行
curl http://localhost:11434/api/tags

# 2. 检查qwen3-vl:8b模型已下载
ollama list | grep qwen3-vl

# 如果没有下载，运行：
ollama pull qwen3-vl:8b
```

### 测试命令

#### 方法1：使用测试脚本（推荐）
```bash
# 测试前3页
./scripts/test_qwen3vl.sh

# 测试指定文件
./scripts/test_qwen3vl.sh "input_file/正文26春初中非常课课通数学8年级人教.pdf" 5
```

#### 方法2：直接使用脚本
```bash
python3 scripts/process_pdf_with_qwen3vl.py \
  "input_file/正文26春初中非常课课通数学8年级人教.pdf" \
  -o output_qwen3vl_test \
  -n 3
```

---

## ⚙️ 配置说明

### Qwen3-VL-8B 配置
```python
{
    "model": "qwen3-vl:8b",
    "api_url": "http://localhost:11434",
    "num_ctx": 65536,      # 64K上下文
    "num_predict": 65536,  # 最大输出64K tokens
    "temperature": 0.1,     # 低温度，稳定输出
    "top_p": 0.9,
    "repeat_penalty": 1.1
}
```

### GLM-4.6V-Flash 配置（对比）
```python
{
    "model": "zai-org/glm-4.6v-flash",
    "api_url": "http://192.168.100.110:9999",
    "max_tokens": 65536,    # 64K tokens
    "temperature": 0.1
}
```

---

## 📊 对比测试方案

### 方案A：快速对比（3页）
```bash
# 1. 测试Qwen3-VL（前3页）
./scripts/test_qwen3vl.sh

# 2. 测试GLM-4.6V（前3页）
python3 scripts/process_pdf_with_glm46v_v2.py \
  "input_file/正文26春初中非常课课通数学8年级人教.pdf" \
  -o output_glm46v_test \
  -n 3

# 3. 对比输出
diff -u output_qwen3vl_test/*_full.md output_glm46v_test/*_full.md
```

### 方案B：完整对比（全部37页）
```bash
# 1. Qwen3-VL处理全部
python3 scripts/process_pdf_with_qwen3vl.py \
  "input_file/正文26春初中非常课课通数学8年级人教.pdf" \
  -o output_qwen3vl_full

# 2. GLM-4.6V处理全部
python3 scripts/process_pdf_with_glm46v_v2.py \
  "input_file/正文26春初中非常课课通数学8年级人教.pdf" \
  -o output_glm46v_full

# 3. 对比质量
```

---

## 🎯 评估指标

### 1. 页眉页脚过滤
- **检查方法**：搜索页码（"第1页"、"Page 1"）
- **期望**：两个模型都应该过滤掉
- **评分**：完全过滤 ⭐⭐⭐⭐⭐

### 2. 注释性双栏处理
- **检查方法**：查找引用块（`> ` 开头）
- **期望**：注释内容正确嵌入主内容
- **评分**：嵌入准确 ⭐⭐⭐⭐⭐⭐

### 3. 题目编号保护
- **检查方法**：搜索【例1】、【例2】
- **期望**：编号完整保留
- **评分**：无遗漏 ⭐⭐⭐⭐⭐☆

### 4. 数学公式LaTeX化
- **检查方法**：查找 `$...$` 和 `$$...$$`
- **期望**：
  - GLM-4.6V：90-95%准确
  - Qwen3-VL：待测试
- **评分**：准确率 ⭐⭐⭐⭐⭐

### 5. 表格分隔行
- **检查方法**：查找 `|---|` 分隔行
- **期望**：所有表格都有分隔行
- **注意**：如果缺失，使用 `fix_markdown_tables.py` 修复
- **评分**：完整性 ⭐⭐⭐⭐☆

### 6. 处理速度
- **测量方法**：总时间 / 总页数
- **期望**：
  - GLM-4.6V：~30-40秒/页
  - Qwen3-VL：待测试（可能更快，本地部署）
- **评分**：速度 ⭐⭐⭐⭐⭐

---

## 🔍 结果记录表

| 指标 | GLM-4.6V | Qwen3-VL | 优胜者 |
|------|----------|----------|--------|
| 页眉页脚过滤 | ⭐⭐⭐⭐⭐ | | |
| 注释性双栏 | ⭐⭐⭐⭐⭐ | | |
| 题目编号 | ⭐⭐⭐⭐⭐ | | |
| 公式LaTeX化 | 90-95% | | |
| 表格分隔行 | ⭐⭐⭐⭐ | | |
| 处理速度 | 30-40s/页 | | |
| **总分** | | | |

---

## 💡 预期优势

### Qwen3-VL-8B 潜在优势
1. **本地部署**：无网络延迟，可能更快
2. **更高分辨率**：百万像素 vs GLM的DPI限制
3. **免费使用**：无API调用成本
4. **生态成熟**：Ollama生态完善

### GLM-4.6V-Flash 已验证优势
1. **公式识别**：复杂符号"全部识别正确"
2. **文档理解**：专门优化过竖排内容
3. **稳定性**：生产环境验证

---

## 🛠️ 故障排除

### Q1: Ollama连接失败
```bash
# 检查Ollama是否运行
ps aux | grep ollama

# 重启Ollama
ollama serve
```

### Q2: 模型未下载
```bash
# 下载qwen3-vl:8b模型
ollama pull qwen3-vl:8b

# 查看已下载模型
ollama list
```

### Q3: 输出截断
**原因**：8K tokens可能不足
**解决**：已配置64K tokens，如仍不足：
```python
# 修改脚本中max_tokens参数
max_tokens=131072  # 提高到128K
```

### Q4: 内存不足
```bash
# 查看Ollama内存占用
ollama ps

# 如果内存不足，降低num_ctx
"num_ctx": 32768  # 改为32K
```

---

## 📝 测试报告模板

```markdown
## Qwen3-VL-8B vs GLM-4.6V-Flash 对比测试

### 测试配置
- 文件：正文26春初中非常课课通数学8年级人教.pdf
- 测试页数：3页（第1-3页）
- 上下文：64K tokens
- 测试时间：2026-02-15

### 结果对比

#### 公式识别
- GLM-4.6V：[准确率]
- Qwen3-VL：[准确率]
- 结论：[ ]

#### 表格处理
- GLM-4.6V：[分隔行正确率]
- Qwen3-VL：[分隔行正确率]
- 结论：[ ]

#### 处理速度
- GLM-4.6V：[秒/页]
- Qwen3-VL：[秒/页]
- 结论：[ ]

### 总体评价
[ ]
```

---

**创建时间**：2026-02-15
**版本**：v1.0
**维护者**：Claude Code Subproject Team
