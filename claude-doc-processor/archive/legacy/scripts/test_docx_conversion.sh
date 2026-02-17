#!/bin/bash
# DOCX转换方法对比测试脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Markdown转DOCX转换方法对比${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查输入文件
if [ $# -lt 1 ]; then
    echo "用法: $0 <markdown文件>"
    exit 1
fi

INPUT_MD="$1"
if [ ! -f "$INPUT_MD" ]; then
    echo "错误：文件不存在 - $INPUT_MD"
    exit 1
fi

# 创建输出目录
OUTPUT_DIR="docx_comparison_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo -e "${YELLOW}输入文件：${NC}$INPUT_MD"
echo -e "${YELLOW}输出目录：${NC}$OUTPUT_DIR"
echo ""

# 方法1：基础pandoc
echo -e "${BLUE}[1/6]${NC} 方法1：基础pandoc转换..."
pandoc "$INPUT_MD" -o "$OUTPUT_DIR/method1_basic.docx" 2>/dev/null
if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_DIR/method1_basic.docx" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 成功 - 大小: $SIZE"
else
    echo -e "  ${RED}✗${NC} 失败"
fi

# 方法2：pandoc + pipe_tables
echo -e "${BLUE}[2/6]${NC} 方法2：pandoc + pipe_tables..."
pandoc "$INPUT_MD" -o "$OUTPUT_DIR/method2_pipe_tables.docx" \
    --from markdown+pipe_tables 2>/dev/null
if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_DIR/method2_pipe_tables.docx" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 成功 - 大小: $SIZE"
else
    echo -e "  ${RED}✗${NC} 失败"
fi

# 方法3：pandoc + grid_tables
echo -e "${BLUE}[3/6]${NC} 方法3：pandoc + grid_tables..."
pandoc "$INPUT_MD" -o "$OUTPUT_DIR/method3_grid_tables.docx" \
    --from markdown+grid_tables+table_captions 2>/dev/null
if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_DIR/method3_grid_tables.docx" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 成功 - 大小: $SIZE"
else
    echo -e "  ${RED}✗${NC} 失败"
fi

# 方法4：pandoc + simple_tables
echo -e "${BLUE}[4/6]${NC} 方法4：pandoc + simple_tables..."
pandoc "$INPUT_MD" -o "$OUTPUT_DIR/method4_simple_tables.docx" \
    --from markdown+simple_tables 2>/dev/null
if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_DIR/method4_simple_tables.docx" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 成功 - 大小: $SIZE"
else
    echo -e "  ${RED}✗${NC} 失败"
fi

# 方法5：python-docx基础版
echo -e "${BLUE}[5/6]${NC} 方法5：python-docx基础版..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/convert_md_to_docx.py" "$INPUT_MD" \
    "$OUTPUT_DIR/method5_python_docx.docx" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_DIR/method5_python_docx.docx" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 成功 - 大小: $SIZE"
else
    echo -e "  ${RED}✗${NC} 失败"
fi

# 方法6：python-docx增强版
echo -e "${BLUE}[6/6]${NC} 方法6：python-docx增强版..."
python3 "$SCRIPT_DIR/convert_md_to_docx_enhanced.py" "$INPUT_MD" \
    "$OUTPUT_DIR/method6_enhanced.docx" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT_DIR/method6_enhanced.docx" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 成功 - 大小: $SIZE"
else
    echo -e "  ${RED}✗${NC} 失败"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}转换完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}输出文件位置：${NC}$OUTPUT_DIR"
echo ""
echo -e "${BLUE}推荐查看顺序：${NC}"
echo "  1. method6_enhanced.docx - python-docx增强版（推荐）"
echo "  2. method5_python_docx.docx - python-docx基础版"
echo "  3. method3_grid_tables.docx - pandoc grid_tables"
echo ""
echo -e "${YELLOW}提示：${NC}在Word或WPS Office中打开，重点检查表格渲染质量"
echo ""
