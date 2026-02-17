#!/bin/bash
# Qwen3-VL-8B PDF识别测试配置
# 专门用于测试Qwen3-VL在数学教辅识别上的表现

# Ollama API配置
export OLLAMA_API_URL="http://localhost:11434"
export QWEN3VL_MODEL="qwen3-vl:8b"

# 生成参数（64K上下文，与GLM-4.6V对比）
export NUM_CTX=65536        # 64K上下文
export NUM_PREDICT=65536    # 最大输出tokens
export TEMPERATURE=0.1      # 低温度，稳定输出
export TOP_P=0.9
export REPEAT_PENALTY=1.1  # 避免重复

# 图片处理配置
export MAX_SIZE=1280        # 最大边长（像素）
export QUALITY=85           # JPEG质量
export COMPRESSION="low"      # low/medium/high
export DPI=200              # PDF转图片的DPI

# 测试配置
export MAX_PAGES=3           # 测试前3页
export START_PAGE=1
export OUTPUT_DIR="output_qwen3vl_test"

echo "✅ Qwen3-VL测试配置已加载"
echo "   模型: $QWEN3VL_MODEL"
echo "   上下文: $NUM_CTX tokens"
echo "   最大输出: $NUM_PREDICT tokens"
echo "   温度: $TEMPERATURE"
echo "   图片质量: ${MAX_SIZE}px, Q${QUALITY}"
