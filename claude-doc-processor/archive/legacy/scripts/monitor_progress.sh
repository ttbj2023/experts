#!/bin/bash
# 监控PDF批处理进度

OUTPUT_DIR="/mnt/wsl/PHYSICALDRIVE2/assistant-experts/claude-doc-processor/output_pdf_batch"

echo "=========================================="
echo "PDF批处理进度监控"
echo "=========================================="

while true; do
    clear
    echo "=========================================="
    echo "PDF批处理进度监控"
    echo "=========================================="
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    # 查找所有处理目录
    dirs=("$OUTPUT_DIR"/*/)
    total_pdfs=3

    if [ ${#dirs[@]} -eq 0 ] || [ ! -d "${dirs[0]}" ]; then
        echo "等待处理开始..."
    else
        for i in "${!dirs[@]}"; do
            dir="${dirs[$i]}"
            dirname=$(basename "$dir")

            # 统计已处理页数
            page_count=$(ls "$dir" 2>/dev/null | grep -E "page_.*\.md$" | wc -l)

            # 从目录名推断PDF名称
            pdf_name=$(echo "$dirname" | sed 's/_[0-9]*$//')

            echo "[$((i+1))/$total_pdfs] $pdf_name"
            echo "    已处理: $page_count 页"
            echo "    状态: $(ls "$dir"/*.md >/dev/null 2>&1 && echo "处理中..." || echo "等待...")"
            echo ""
        done
    fi

    echo "=========================================="
    echo "按 Ctrl+C 退出监控"
    echo "=========================================="

    sleep 10
done
