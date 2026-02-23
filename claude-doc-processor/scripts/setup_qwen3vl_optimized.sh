#!/bin/bash
# Qwen3 VL 8B 优化模型部署脚本
# 针对 RTX 4070 TiS 16GB 显存优化

set -e

echo "======================================"
echo "Qwen3 VL 8B 优化模型部署"
echo "======================================"

# 检查 Ollama 是否运行
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama 未运行，请先启动 Ollama"
    echo "   启动命令: ollama serve"
    exit 1
fi

echo "✅ Ollama 运行中"

# 检查基础模型是否存在
echo ""
echo "检查基础模型 qwen3-vl:8b ..."
if ! ollama list | grep -q "qwen3-vl:8b"; then
    echo "⚠️  基础模型未找到，正在拉取..."
    ollama pull qwen3-vl:8b
else
    echo "✅ 基础模型已存在"
fi

# 创建优化的 Modelfile
echo ""
echo "创建优化配置..."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELFILE_PATH="$PROJECT_ROOT/config/Modelfile_qwen3vl_8b"

cat > "$MODELFILE_PATH" << 'EOF'
# Qwen3 VL 8B - 文档处理优化版
# 针对 RTX 4070 TiS 16GB 显存优化

FROM qwen3-vl:8b

# 12K 上下文窗口（标准配置）⭐ 推荐
# Token 计算：视觉Token = (宽×高) / (32×32) + 2
# 1080p 图片：~2100 视觉Token
# 完整请求：视觉(2.1K) + 提示(0.5K) + 思考(4K) + 输出(2K) ≈ 8.5K
# 预留余量：12K - 8.5K ≈ 3.5K (40% 安全余量)
PARAMETER num_ctx 12284

# 温度参数（场景化）
# 默认使用 0.1，可根据场景调整
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40

# 显存优化
PARAMETER num_batch 512

# 停止词
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|end|>"
PARAMETER stop "<|eot_id|>"

# 系统模板
TEMPLATE """
{{- if .System }}
<|im_start|>system
{{ .System }}<|im_end|>
{{- end }}

{{- range .Messages }}
<|im_start|>{{ .Role }}
{{ .Content }}<|im_end|>
{{- end }}

<|im_start|>assistant
"""
EOF

echo "✅ Modelfile 已创建: $MODELFILE_PATH"

# 创建自定义模型
echo ""
echo "创建自定义模型 qwen3-vl-8b-doc ..."
if ollama create qwen3-vl-8b-doc -f "$MODELFILE_PATH"; then
    echo "✅ 模型创建成功"
else
    echo "❌ 模型创建失败"
    exit 1
fi

# 验证模型
echo ""
echo "验证模型..."
if ollama list | grep -q "qwen3-vl-8b-doc"; then
    echo "✅ 模型已就绪"
    echo ""
    echo "======================================"
    echo "模型信息"
    echo "======================================"
    ollama show qwen3-vl-8b-doc
else
    echo "❌ 模型验证失败"
    exit 1
fi

# 更新配置文件
echo ""
echo "更新配置文件..."
CONFIG_FILE="$PROJECT_ROOT/config/default.yaml"

if [ -f "$CONFIG_FILE" ]; then
    # 备份原配置
    cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
    echo "✅ 原配置已备份: $CONFIG_FILE.bak"

    # 更新模型名称（使用 sed）
    if sed -i 's/vision_model: "qwen3-vl:8b"/vision_model: "qwen3-vl-8b-doc"/' "$CONFIG_FILE"; then
        echo "✅ 配置已更新"
    else
        echo "⚠️  请手动更新配置文件中的 vision_model 为 'qwen3-vl-8b-doc'"
    fi
fi

echo ""
echo "======================================"
echo "部署完成！"
echo "======================================"
echo ""
echo "模型: qwen3-vl-8b-doc"
echo "上下文: 12K tokens (标准配置) ⭐"
echo "温度: 0.1"
echo ""
echo "Token 计算:"
echo "  1080p图片 ≈ 2100 视觉Token"
echo "  完整请求 ≈ 8.5K (视觉2K + 提示0.5K + 思考4K + 输出2K)"
echo "  安全余量 ≈ 3.5K (40%)"
echo ""
echo "使用方法:"
echo "  1. 确认 Ollama 正在运行"
echo "  2. 启动模型: ollama run qwen3-vl-8b-doc"
echo "  3. 测试: ./convert.py document.pdf -o output/"
echo ""
echo "参数调整参考:"
echo "  - 720p图片: num_ctx 8192"
echo "  - 1080p图片: num_ctx 12288 (推荐) ⭐"
echo "  - 2K图片: num_ctx 16384"
echo "  - 4K图片: num_ctx 24576"
echo ""
echo "场景化温度:"
echo "  - OCR(高精度): temperature 0.05"
echo "  - 描述(平衡): temperature 0.2"
echo "  - 分类(严格): temperature 0.0"
echo "  - 匹配(全局): temperature 0.1"
echo ""
