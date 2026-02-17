#!/bin/bash
# 数学教辅PDF处理快速测试脚本（v3提示词）
# 用途：快速测试新提示词在少量页面上的效果

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}数学教辅PDF处理 v3 提示词测试${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 配置参数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INPUT_FILE="${1:-}"
MAX_PAGES="${2:-3}"
OUTPUT_DIR="${PROJECT_ROOT}/output_test_v3"

# 检查输入文件
if [ -z "$INPUT_FILE" ]; then
    echo -e "${YELLOW}用法: $0 <PDF文件路径> [测试页数]${NC}"
    echo ""
    echo "示例："
    echo "  $0 input_file/教材.pdf 3      # 测试前3页"
    echo "  $0 input_file/教材.pdf 5      # 测试前5页"
    echo "  $0 input_file/教材.pdf 10     # 测试前10页"
    echo ""
    echo -e "${YELLOW}默认测试文件：@input_file/正文26春初中非常课课通数学8年级人教.pdf${NC}"
    echo ""
    exit 1
fi

# 检查文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}错误：文件不存在 - $INPUT_FILE${NC}"
    exit 1
fi

# 显示测试配置
echo -e "${YELLOW}测试配置：${NC}"
echo "  输入文件：$INPUT_FILE"
echo "  测试页数：$MAX_PAGES"
echo "  输出目录：$OUTPUT_DIR"
echo "  脚本：process_pdf_with_glm46v_v2.py（已内置v3提示词）"
echo ""

# 确认执行
read -p "开始测试？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消测试"
    exit 0
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo ""
echo -e "${GREEN}开始处理...${NC}"
echo ""

# 执行处理
cd "$PROJECT_ROOT"
python3 scripts/process_pdf_with_glm46v_v2.py \
  --input "$INPUT_FILE" \
  --output "$OUTPUT_DIR" \
  --max-pages "$MAX_PAGES"

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ 测试完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}输出文件位置：${NC}"
    ls -lh "$OUTPUT_DIR"/*.md 2>/dev/null || echo "  未找到Markdown文件"
    echo ""
    echo -e "${YELLOW}验证检查项：${NC}"
    echo "  1. 页眉页脚是否已去除？"
    echo "  2. 注释是否用引用块（>）标记？"
    echo "  3. 题目编号是否完整？"
    echo "  4. 公式是否LaTeX化（$...$ 或 $$...$$）？"
    echo "  5. 是否没有代码块（```）？"
    echo ""
    echo -e "${YELLOW}查看输出文件：${NC}"
    echo "  cat $OUTPUT_DIR/*.md"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ 测试失败${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "请检查："
    echo "  1. GLM-4.6V API服务是否正常运行"
    echo "  2. 网络连接是否正常"
    echo "  3. PDF文件是否损坏"
    echo ""
    exit 1
fi
