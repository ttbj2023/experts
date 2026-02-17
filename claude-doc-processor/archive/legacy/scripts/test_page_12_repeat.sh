#!/bin/bash
# 重复测试第12页，验证LaTeX问题复现频率

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}重复测试第12页（5次）${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INPUT_FILE="input_file/正文26春初中非常课课通数学8年级人教.pdf"
OUTPUT_BASE="output_test_page12_repeat"
TOTAL_TESTS=5

# 清理旧输出
rm -rf "$OUTPUT_BASE"
mkdir -p "$OUTPUT_BASE"

echo -e "${YELLOW}测试配置：${NC}"
echo "  输入文件：$INPUT_FILE"
echo "  测试页数：第12页"
echo "  重复次数：$TOTAL_TESTS"
echo "  输出目录：$OUTPUT_BASE"
echo ""

# 创建处理器类名
if [ -f "$SCRIPT_DIR/process_pdf_with_qwen3vl.py" ]; then
    PROCESSOR="process_pdf_with_qwen3vl.py"
    MODEL_NAME="Qwen3-VL-8B"
    API_ARG="--api-url http://localhost:11434"
else
    PROCESSOR="process_pdf_with_glm46v_v2.py"
    MODEL_NAME="GLM-4.6V-Flash"
    API_ARG=""
fi

echo -e "${BLUE}使用模型：${NC}$MODEL_NAME"
echo ""

# 记录每次测试的结果
declare -a HAS_PROBLEM
declare -a NO_PROBLEM

# 重复测试
for i in $(seq 1 $TOTAL_TESTS); do
    echo ""
    echo -e "${YELLOW}======================================${NC}"
    echo -e "${YELLOW}第 $i 次测试${NC}"
    echo -e "${YELLOW}======================================${NC}"
    echo ""
    
    OUTPUT_DIR="${OUTPUT_BASE}/test_${i}"
    mkdir -p "$OUTPUT_DIR"
    
    # 处理
    echo -e "🔄 处理中...${NC}"
    python3 "$SCRIPT_DIR/$PROCESSOR" \
        $API_ARG \
        --input "$INPUT_FILE" \
        --output "$OUTPUT_DIR" \
        -s 12 \
        -n 1 > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        OUTPUT_FILE=$(find "$OUTPUT_DIR" -name "*_full.md" | head -1)
        
        if [ -n "$OUTPUT_FILE" ]; then
            # 检查是否有LaTeX渲染问题
            if grep -q '\\text{' "$OUTPUT_FILE"; then
                if grep -q '\\because' "$OUTPUT_FILE"; then
                    if grep -q '\\therefore' "$OUTPUT_FILE"; then
                        echo -e "${RED}❌ 检测到LaTeX渲染问题${NC}"
                        echo -e "   \\text{、\\because、\\therefore 同时出现"
                        HAS_PROBLEM+=("$OUTPUT_FILE")
                    fi
                fi
            fi
            
            # 如果没有问题
            if [ ${#HAS_PROBLEM[@]} -eq $((i-1)) ]; then
                NO_PROBLEM+=("$OUTPUT_FILE")
            fi
        else
            echo -e "${RED}❌ 输出文件未找到${NC}"
        fi
    else
        echo -e "${RED}❌ 处理失败${NC}"
    fi
done

# 统计结果
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}测试结果统计${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

PROBLEM_COUNT=${#HAS_PROBLEM[@]}
NO_PROBLEM_COUNT=${#NO_PROBLEM[@]}

echo -e "${YELLOW}总测试次数：${NC}$TOTAL_TESTS"
echo -e "${YELLOW}出现问题次数：${NC}$PROBLEM_COUNT"
echo -e "${YELLOW}无问题次数：${NC}$NO_PROBLEM_COUNT"
echo ""

if [ $PROBLEM_COUNT -gt 0 ]; then
    echo -e "${RED}❌ 出现问题的测试：${NC}"
    for i in "${!HAS_PROBLEM[@]}"; do
        echo -e "  ${RED}测试 #$i${NC}: ${HAS_PROBLEM[$i]}"
    done
    echo ""
fi

if [ $NO_PROBLEM_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ 无问题的测试：${NC}"
    for i in "${!NO_PROBLEM[@]}"; do
        echo -e "  ${GREEN}测试 #$i${NC}: ${NO_PROBLEM[$i]}"
    done
    echo ""
fi

# 结论
echo -e "${BLUE}问题复现率：${NC}$PROBLEM_COUNT/$TOTAL_TESTS ($(python3 -c "print(f'{%.1f}', ($PROBLEM_COUNT/$TOTAL_TESTS * 100))")")"
echo ""

if [ $PROBLEM_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ 结论：问题极不稳定，可能是偶发${NC}"
elif [ $PROBLEM_COUNT -le 2 ]; then
    echo -e "${YELLOW}⚠️  结论：问题偶尔出现（低频）${NC}"
else
    echo -e "${RED}❌ 结论：问题稳定复现（高频）${NC}"
fi
