#!/bin/bash
# MinerU服务调用脚本
#
# 功能：调用MinerU HTTP API将PDF/DOCX转换为Markdown
# 输入：文件路径（第一个参数）
# 输出：JSON格式的转换结果（包含markdown内容和图片）
#
# 使用方法：
#   ./scripts/call_mineru.sh /path/to/document.pdf
#
# 环境变量：
#   MINERU_API_URL: MinerU服务地址（默认：http://localhost:8177）
#   OUTPUT_DIR: 输出目录（默认：/tmp/mineru_output）
#   LANG_LIST: 语言列表（默认：ch，中文/英文）
#   BACKEND: 解析后端（默认：pipeline）

set -e  # 遇到错误立即退出

# 获取输入文件路径
INPUT_FILE="${1:-}"

# 验证输入文件
if [ -z "$INPUT_FILE" ]; then
    echo "错误: 未提供输入文件路径" >&2
    echo "使用方法: $0 <input_file>" >&2
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "错误: 输入文件不存在: $INPUT_FILE" >&2
    exit 1
fi

# MinerU服务地址（适配实际API）
MINERU_API_URL="${MINERU_API_URL:-http://localhost:8177}"

# 输出目录
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/mineru_output}"
mkdir -p "$OUTPUT_DIR"

# 语言列表（ch: 中文/英文，en: 英文）
LANG_LIST="${LANG_LIST:-ch}"

# 解析后端（pipeline: 通用多语言，hybrid-auto-engine: 下一代高精度）
BACKEND="${BACKEND:-pipeline}"

echo "调用MinerU服务..."
echo "输入文件: $INPUT_FILE"
echo "服务地址: $MINERU_API_URL"
echo "输出目录: $OUTPUT_DIR"
echo "语言设置: $LANG_LIST"
echo "解析后端: $BACKEND"

# 输出临时文件（用于保存响应）
OUTPUT_JSON="/tmp/mineru_response_$(date +%s).json"

# 调用MinerU API（适配实际端点/参数）
HTTP_CODE=$(curl -X POST \
    "$MINERU_API_URL/file_parse" \
    -F "files=@$INPUT_FILE" \
    -F "output_dir=$OUTPUT_DIR" \
    -F "lang_list=$LANG_LIST" \
    -F "backend=$BACKEND" \
    -F "parse_method=auto" \
    -F "formula_enable=true" \
    -F "table_enable=true" \
    -o "$OUTPUT_JSON" \
    -w "%{http_code}" \
    --silent \
    --show-error \
    --connect-timeout 30 \
    --max-time 300)

# 检查HTTP状态码
if [ "$HTTP_CODE" -ne 200 ]; then
    echo "错误: MinerU API调用失败 (HTTP $HTTP_CODE)" >&2
    if [ -f "$OUTPUT_JSON" ]; then
        echo "响应内容: $(cat "$OUTPUT_JSON")" >&2
        rm -f "$OUTPUT_JSON"
    fi
    exit 1
fi

# 输出目录路径（包含解析结果）
echo "$OUTPUT_DIR"

# 输出JSON响应路径（供调用者使用）
echo "$OUTPUT_JSON"
