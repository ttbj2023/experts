#!/bin/bash
# 快速批量转换Markdown为DOCX（增强版）

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# 检查依赖
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误：未找到python3${NC}"
    exit 1
fi

if ! python3 -c "import docx" 2>/dev/null; then
    echo -e "${RED}错误：未安装python-docx库${NC}"
    echo -e "${YELLOW}安装命令：pip3 install python-docx${NC}"
    exit 1
fi

# 显示帮助
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "用法: $0 <markdown文件或目录> [输出目录]"
    echo ""
    echo "示例:"
    echo "  $0 document.md                    # 转换单个文件"
    echo "  $0 document.md output.docx        # 指定输出文件名"
    echo "  $0 .                             # 转换当前目录所有MD文件"
    echo "  $0 docs/ output/                 # 批量转换并指定输出目录"
    echo ""
    echo "特性:"
    echo "  ✓ 增强的表格样式（边框、背景色、自动对齐）"
    echo "  ✓ 表头加粗和白色文字"
    echo "  ✓ 交替行背景色（斑马纹）"
    echo "  ✓ 中文字体支持（宋体、黑体）"
    echo "  ✓ 数学公式字体（Cambria Math）"
    echo "  ✓ 代码块样式（Consolas等宽字体）"
    exit 0
fi

INPUT="$1"
OUTPUT_DIR="${2:-.}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERTER="$SCRIPT_DIR/convert_md_to_docx_enhanced.py"

# 检查转换器是否存在
if [ ! -f "$CONVERTER" ]; then
    echo -e "${RED}错误：未找到转换器 - $CONVERTER${NC}"
    exit 1
fi

# 处理单个文件
if [ -f "$INPUT" ]; then
    # 检查文件扩展名
    if [[ ! "$INPUT" =~ \.md$ ]] && [[ ! "$INPUT" =~ \.markdown$ ]]; then
        echo -e "${RED}错误：输入文件必须是Markdown格式（.md或.markdown）${NC}"
        exit 1
    fi

    # 确定输出文件
    if [ -n "$2" ] && [[ "$2" =~ \.docx$ ]]; then
        OUTPUT_FILE="$2"
    else
        INPUT_BASE=$(basename "$INPUT")
        OUTPUT_FILE="${OUTPUT_DIR}/${INPUT_BASE%.md}.docx"
        OUTPUT_FILE="${OUTPUT_FILE%.markdown}.docx"
    fi

    echo -e "${BLUE}转换中...${NC}"
    echo "  输入: $INPUT"
    echo "  输出: $OUTPUT_FILE"

    python3 "$CONVERTER" "$INPUT" "$OUTPUT_FILE"

    if [ $? -eq 0 ]; then
        SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo -e "${GREEN}✓ 转换成功！文件大小：$SIZE${NC}"
    else
        echo -e "${RED}✗ 转换失败${NC}"
        exit 1
    fi

# 处理目录（批量转换）
elif [ -d "$INPUT" ]; then
    echo -e "${BLUE}批量转换目录：$INPUT${NC}"
    echo ""

    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"

    # 计数器
    SUCCESS=0
    FAILED=0
    TOTAL=0

    # 遍历所有MD文件
    while IFS= read -r -d '' md_file; do
        ((TOTAL++))

        INPUT_BASE=$(basename "$md_file")
        OUTPUT_FILE="${OUTPUT_DIR}/${INPUT_BASE%.md}.docx"

        echo -ne "${BLUE}[${TOTAL}]${NC} 转换: ${INPUT_BASE}... "

        python3 "$CONVERTER" "$md_file" "$OUTPUT_FILE" >/dev/null 2>&1

        if [ $? -eq 0 ]; then
            SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
            echo -e "${GREEN}✓${NC} (${SIZE})"
            ((SUCCESS++))
        else
            echo -e "${RED}✗${NC}"
            ((FAILED++))
        fi
    done < <(find "$INPUT" -maxdepth 1 -type f \( -name "*.md" -o -name "*.markdown" \) -print0)

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}批量转换完成${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "总计: ${TOTAL} 个文件"
    echo -e "${GREEN}成功: ${SUCCESS} 个${NC}"
    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}失败: ${FAILED} 个${NC}"
    fi
    echo ""

else
    echo -e "${RED}错误：输入路径不存在 - $INPUT${NC}"
    exit 1
fi
