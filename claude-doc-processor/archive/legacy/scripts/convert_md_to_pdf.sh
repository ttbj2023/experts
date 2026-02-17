#!/bin/bash
# 直接使用 Pandoc 将 GLM 输出转换为 PDF
# 不需要 Ollama 或其他 LLM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    cat << EOF
用法: $0 <md_file> [选项]

参数:
    <md_file>    Markdown 文件路径（支持通配符）

选项:
    -o, --output FILE    输出 PDF 文件名（默认：input.pdf）
    -f, --font FONT     中文字体（默认：SimSun）

示例:
    # 转换单个文件
    $0 page_001.md -o chapter1.pdf

    # 转换完整文档
    $0 document_full.md -o complete_book.pdf

    # 使用中文字体
    $0 page_002.md -o output.pdf -f "SimSun"
EOF
    exit 1
}

# 解析参数
OUTPUT_FILE="input.pdf"
FONT="SimSun"

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_FILE="$2"
            shift
            ;;
        -f|--font)
            FONT="$2"
            shift
            ;;
        *)
            MD_FILE="$1"
            ;;
    esac
    shift
done

if [[ $# -eq 0 ]]; then
    show_help
fi

MD_FILE="$1"

# 检查文件是否存在
if [[ ! -f "$MD_FILE" ]]; then
    echo "❌ 错误：文件不存在: $MD_FILE"
    exit 1
fi

# 获取输入文件名（不含扩展）
BASENAME=$(basename "$MD_FILE" .md)

echo "📄 输入文件: $MD_FILE"
echo "   大小: $(wc -c < "$MD_FILE") 字符"
echo ""
echo "🔄 调用 Pandoc 转换为 PDF..."
echo ""

# 构建 pandoc 命令
PANDOC_CMD="pandoc \"$MD_FILE\" \
  -o \"$OUTPUT_FILE\" \
  --pdf-engine=xelatex \
  -V CJKmainfont=\"$FONT\" \
  -V geometry:margin=1cm \
  --variable CJKmainfont=\"${FONT}\" \
  -f hindi \
  -f arabic \
  --toc"

echo "执行："
echo "$PANDOC_CMD"
echo ""

# 执行转换
start_time=$(date +%s)
eval $PANDOC_CMD
exit_code=$?
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))

if [[ $exit_code -eq 0 ]]; then
    echo "✅ 转换成功！"
    echo "   📄 输出文件: $OUTPUT_FILE"
    echo "   📊 文件大小: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
    echo "   ⏱ 耗时: ${elapsed_time}s"
else
    echo "❌ 转换失败（退出码: $exit_code）"
    exit $exit_code
fi

echo ""
echo "💡 提示："
echo "   - 可以使用 --font 选项指定其他中文字体"
echo "   - 中文常用字体：SimSun（宋体）、SimHei（黑体）、KaiTi（楷体）、FangSong（仿宋）"
echo "   - 查看PDF效果：xdg-open \"$OUTPUT_FILE\" 2>/dev/null &"
