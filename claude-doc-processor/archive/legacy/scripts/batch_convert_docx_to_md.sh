#!/bin/bash
# 批量转换DOCX文件为Markdown格式

set -e  # 遇到错误立即退出

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="${INPUT_DIR:-/mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor/input_file}"
OUTPUT_DIR="${OUTPUT_DIR:-/mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor/output_docx_to_md}"
CONVERTER_SCRIPT="${SCRIPT_DIR}/convert_docx_to_markdown.py"
LOG_FILE="${OUTPUT_DIR}/conversion_log.md"
IMAGE_QUALITY="${IMAGE_QUALITY:-85}"
OPTIMIZE_IMAGES="${OPTIMIZE_IMAGES:-true}"

# 创建输出目录
mkdir -p "${OUTPUT_DIR}"

# 初始化日志
init_log() {
    cat > "${LOG_FILE}" << EOF
# DOCX to Markdown 批量转换日志

转换时间: $(date '+%Y-%m-%d %H:%M:%S')
输入目录: \`${INPUT_DIR}\`
输出目录: \`${OUTPUT_DIR}\`
图片质量: ${IMAGE_QUALITY}
图片优化: ${OPTIMIZE_IMAGES}

## 转换统计

| 文件名 | 状态 | 图片数 | 公式数 | LaTeX转换 | 降级图片 | 处理时间 |
|--------|------|--------|--------|-----------|----------|----------|

EOF
}

# 添加转换记录到日志
log_result() {
    local file_name="$1"
    local status="$2"
    local images="$3"
    local formulas="$4"
    local latex_conv="$5"
    local fallback="$6"
    local time="$7"

    echo "| ${file_name} | ${status} | ${images} | ${formulas} | ${latex_conv} | ${fallback} | ${time}s |" >> "${LOG_FILE}"
}

# 查找所有DOCX文件
find_docx_files() {
    find "${INPUT_DIR}" -maxdepth 1 -type f -name "*.docx" | sort
}

# 转换单个文件
convert_file() {
    local docx_file="$1"
    local base_name=$(basename "${docx_file}")
    local file_name="${base_name%.docx}"

    echo "========================================"
    echo "正在转换: ${base_name}"
    echo "========================================"

    # 执行转换
    local start_time=$(date +%s)

    if [ "${OPTIMIZE_IMAGES}" = "true" ]; then
        python3 "${CONVERTER_SCRIPT}" "${docx_file}" \
            -o "${OUTPUT_DIR}" \
            --quality "${IMAGE_QUALITY}"
    else
        python3 "${CONVERTER_SCRIPT}" "${docx_file}" \
            -o "${OUTPUT_DIR}" \
            --no-optimize
    fi

    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 检查是否成功
    if [ ${exit_code} -eq 0 ]; then
        # 读取元数据
        local meta_file="${OUTPUT_DIR}/${file_name}/meta.json"
        if [ -f "${meta_file}" ]; then
            local images=$(python3 -c "import json; print(json.load(open('${meta_file}')).get('total_images', 0))" 2>/dev/null || echo "0")
            local formulas=$(python3 -c "import json; print(json.load(open('${meta_file}')).get('total_formulas', 0))" 2>/dev/null || echo "0")
            local latex_conv=$(python3 -c "import json; print(json.load(open('${meta_file}')).get('converted_formulas', 0))" 2>/dev/null || echo "0")
            local fallback=$(python3 -c "import json; print(json.load(open('${meta_file}')).get('fallback_images', 0))" 2>/dev/null || echo "0")

            echo "✓ 转换成功！"
            echo "  图片: ${images} 张"
            echo "  公式: ${formulas} 个"
            echo "  LaTeX转换: ${latex_conv} 个"
            echo "  降级图片: ${fallback} 个"
            echo "  处理时间: ${duration} 秒"

            log_result "${file_name}" "✓ 成功" "${images}" "${formulas}" "${latex_conv}" "${fallback}" "${duration}"
        else
            echo "✓ 转换成功（未找到元数据文件）"
            log_result "${file_name}" "✓ 成功" "-" "-" "-" "-" "${duration}"
        fi
    else
        echo "✗ 转换失败，退出码: ${exit_code}"
        log_result "${file_name}" "✗ 失败" "-" "-" "-" "-" "${duration}"
    fi

    echo ""
}

# 主函数
main() {
    echo "=========================================="
    echo "DOCX to Markdown 批量转换工具"
    echo "=========================================="
    echo "输入目录: ${INPUT_DIR}"
    echo "输出目录: ${OUTPUT_DIR}"
    echo "图片质量: ${IMAGE_QUALITY}"
    echo "图片优化: ${OPTIMIZE_IMAGES}"
    echo "=========================================="
    echo ""

    # 检查转换脚本
    if [ ! -f "${CONVERTER_SCRIPT}" ]; then
        echo "错误: 未找到转换脚本 ${CONVERTER_SCRIPT}"
        exit 1
    fi

    # 初始化日志
    init_log

    # 查找所有DOCX文件
    local docx_files=($(find_docx_files))
    local total_files=${#docx_files[@]}

    if [ ${total_files} -eq 0 ]; then
        echo "警告: 未找到任何DOCX文件"
        exit 0
    fi

    echo "找到 ${total_files} 个DOCX文件"
    echo ""

    # 转换每个文件
    local current=0
    for docx_file in "${docx_files[@]}"; do
        current=$((current + 1))
        echo "[${current}/${total_files}] 处理中..."

        convert_file "${docx_file}"
    done

    echo "=========================================="
    echo "批量转换完成！"
    echo "=========================================="
    echo "总文件数: ${total_files}"
    echo "日志文件: ${LOG_FILE}"
    echo "输出目录: ${OUTPUT_DIR}"
    echo "=========================================="
}

# 执行主函数
main
