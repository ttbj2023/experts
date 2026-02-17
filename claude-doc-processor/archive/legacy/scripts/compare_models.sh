#!/bin/bash
# Qwen3-VL vs GLM-4.6V 对比测试脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Qwen3-VL vs GLM-4.6V 对比测试${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INPUT_FILE="${1:-input_file/正文26春初中非常课课通数学8年级人教.pdf}"
MAX_PAGES="${2:-5}"

echo -e "${YELLOW}测试配置：${NC}"
echo "  输入文件：$INPUT_FILE"
echo "  测试页数：$MAX_PAGES"
echo ""

# 检查文件
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}错误：文件不存在 - $INPUT_FILE${NC}"
    exit 1
fi

# 检查Ollama
echo -e "${BLUE}检查Ollama服务...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}错误：Ollama服务未运行！${NC}"
    echo "请先启动：ollama serve"
    exit 1
fi
echo -e "${GREEN}✅ Ollama服务正常${NC}"
echo ""

# 确认
read -p "开始对比测试？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消测试"
    exit 0
fi

# 清理旧输出
rm -rf output_compare_qwen3vl output_compare_glm46v
mkdir -p output_compare_qwen3vl output_compare_glm46v

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}第1步：测试 Qwen3-VL-8B${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

time_start_qwen=$(date +%s)
python3 "$SCRIPT_DIR/process_pdf_with_qwen3vl.py" \
    --api-url http://localhost:11434 \
    --input "$INPUT_FILE" \
    --output output_compare_qwen3vl \
    --max-pages "$MAX_PAGES"
time_end_qwen=$(date +%s)
time_qwen=$((time_end_qwen - time_start_qwen))

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}第2步：测试 GLM-4.6V-Flash${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

time_start_glm=$(date +%s)
python3 "$SCRIPT_DIR/process_pdf_with_glm46v_v2.py" \
    --input "$INPUT_FILE" \
    --output output_compare_glm46v \
    --max-pages "$MAX_PAGES"
time_end_glm=$(date +%s)
time_glm=$((time_end_glm - time_start_glm))

# 统计
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}测试完成！对比统计${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}处理速度：${NC}"
echo "  Qwen3-VL: ${time_qwen}秒 ($((time_qwen / MAX_PAGES))秒/页)"
echo "  GLM-4.6V:  ${time_glm}秒 ($((time_glm / MAX_PAGES))秒/页)"
echo ""

# 查找输出文件
qwen_md=$(find output_compare_qwen3vl -name "*_full.md" 2>/dev/null | head -1)
glm_md=$(find output_compare_glm46v -name "*_full.md" 2>/dev/null | head -1)

if [ -n "$qwen_md" ] && [ -n "$glm_md" ]; then
    echo -e "${YELLOW}输出文件：${NC}"
    echo "  Qwen3-VL: $qwen_md"
    echo "  GLM-4.6V:  $glm_md"
    echo ""
    echo -e "${YELLOW}查看对比：${NC}"
    echo "  diff -u $glm_md $qwen_md"
    echo ""
    echo -e "${YELLOW}或在浏览器中打开：${NC}"
    echo "  Qwen3-VL: file://$(pwd)/$qwen_md"
    echo "  GLM-4.6V:  file://$(pwd)/$glm_md"
fi

echo ""
echo -e "${GREEN}✅ 对比完成！${NC}"
echo ""
echo -e "${YELLOW}下一步：${NC}"
echo "  1. 检查公式识别准确率"
echo "  2. 验证表格分隔行完整性"
echo "  3. 评估页眉页脚过滤效果"
echo "  4. 检查注释性双栏处理质量"
