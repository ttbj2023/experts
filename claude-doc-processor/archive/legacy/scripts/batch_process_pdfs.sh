#!/bin/bash
# 批量处理 input_file 目录下的所有PDF文件

cd "/mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor"

PDF_DIR="input_file"
OUTPUT_DIR="output_pdf_batch"
SCRIPT_DIR="scripts"
PYTHON_BIN=".venv/bin/python"
API_URL="http://192.168.100.110:9999"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 获取所有PDF文件
PDFS=("$PDF_DIR"/*.pdf)

echo "=========================================="
echo "开始批量处理 PDF 文件"
echo "共 ${#PDFS[@]} 个文件"
echo "=========================================="

# 逐个处理
for i in "${!PDFS[@]}"; do
    pdf="${PDFS[$i]}"
    filename=$(basename "$pdf")
    num=$((i + 1))

    echo ""
    echo "[$num/${#PDFS[@]}] 处理: $filename"
    echo "----------------------------------------"

    # 调用处理脚本
    $PYTHON_BIN "$SCRIPT_DIR/process_pdf_with_glm46v_v2.py" \
        "$pdf" \
        -o "$OUTPUT_DIR" \
        --api-url "$API_URL"

    if [ $? -eq 0 ]; then
        echo "✓ $filename 处理成功"
    else
        echo "✗ $filename 处理失败"
    fi
done

echo ""
echo "=========================================="
echo "批量处理完成！"
echo "输出目录: $OUTPUT_DIR"
echo "=========================================="
