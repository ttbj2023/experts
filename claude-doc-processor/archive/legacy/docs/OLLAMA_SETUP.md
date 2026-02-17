# 使用 Ollama 运行 GLM-4.6V-Flash 模型

## 安装 Ollama

### Linux/WSL
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 验证安装
```bash
ollama --version
```

## 拉取 GLM-4.6V-Flash 模型

```bash
# Q4_K_M 量化版本 (推荐)
ollama pull doitmagic/glm-4.6v-flash:q4_k_m

# 或者查看可用版本
ollama search glm-4.6v
```

## 启动 Ollama 服务

```bash
# 后台运行
ollama serve &

# 或者指定端口（避免与其他服务冲突）
ollama serve --port 11434 &

# 验证服务
curl http://localhost:11434/api/tags
```

## 测试模型运行

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "doitmagic/glm-4.6v-flash:q4_k_m",
  "messages": [{"role": "user", "content": "1+1=几？只回答数字。"}],
  "stream": false
}'
```

## 修改格式化脚本使用 Ollama

创建新脚本：`scripts/format_with_ollama.py`

关键配置：
```python
API_URL = "http://localhost:11434"  # Ollama 默认端口
MODEL_NAME = "doitmagic/glm-4.6v-flash:q4_k_m"
```

## 优势

✅ **完全本地运行** - 无需 LM Studio
✅ **模型切换简单** - 直接 pull 不同模型
✅ **API 兼容 OpenAI** - 可以复用现有脚本
✅ **资源占用明确** - 可以看到实际内存/CPU使用
✅ **完全离线** - 不依赖外部API

## 完整工作流

1. 安装 Ollama
2. 拉取模型：`ollama pull doitmagic/glm-4.6v-flash:q4_k_m`
3. 启动服务：`ollama serve --port 11434`
4. 运行格式化：`python3 scripts/format_with_ollama.py output_xxx.md`

---

**是否需要我创建 format_with_ollama.py 脚本？**
