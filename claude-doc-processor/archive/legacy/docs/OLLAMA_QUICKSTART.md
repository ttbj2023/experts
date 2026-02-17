# Ollama + GLM-4.6V 快速开始

## 步骤 1：安装 Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

验证安装：
```bash
ollama --version
```

## 步骤 2：拉取 GLM-4.6V 模型

```bash
# Q4_K_M 量化版本（推荐，约 4GB）
ollama pull doitmagic/glm-4.6v-flash:q4_k_m

# 查看下载进度
ollama list
```

## 步骤 3：启动 Ollama 服务

```bash
# 后台运行（推荐）
ollama serve &

# 查看日志确认服务启动
# 应该看到 "Serving on http://127.0.0.11434"
```

## 步骤 4：测试运行

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "doitmagic/glm-4.6v-flash:q4_k_m",
  "prompt": "1+1等于几？"
}'
```

应该返回：`2`

## 步骤 5：批量格式化您的 5 页 PDF

```bash
# 进入项目目录
cd /mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor

# 批量格式化所有5页
for i in {1..5}; do
  echo "🔄 格式化第 ${i} 页..."
  python3 scripts/format_with_ollama.py \
    "output_glm_5pages/*/page_00${i}.md"
done

echo "✅ 全部完成！"
```

## 常见问题

**Q: 如何查看 Ollama 运行的模型？**
A: `ollama list`

**Q: 如何停止 Ollama？**
A: `pkill ollama` 或 Ctrl+C（如果前台运行）

**Q: 如何更换其他模型？**
A:
```bash
# 拉取其他模型
ollama pull qwen2.5:7b

# 修改脚本中的 --model 参数
python3 scripts/format_with_ollama.py xxx.md --model qwen2.5:7b
```

**Q: 内存不足怎么办？**
A: 使用更小的量化版本：
```bash
ollama pull doitmagic/glm-4.6v-flash:q4_k_m  # Q4_K_M
ollama pull doitmagic/glm-4.6v-flash:q4_0k    # Q4_0K (更小)
```

## 优势对比

| 特性 | Ollama | LM Studio |
|------|---------|------------|
| 完全本地 | ✅ | ❌ (需GUI）|
| 模型切换 | 快速命令 | 需手动操作 |
| 资源监控 | 明确 | 不直观 |
| 端口冲突 | 可自定义 | 固定9999 |
| API 兼容 | OpenAI | LM Studio特有 |

---

**准备好了吗？开始步骤1吧！** 🚀
