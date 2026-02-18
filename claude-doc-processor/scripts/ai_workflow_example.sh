#!/bin/bash
# AI集成工作流示例脚本
#
# 功能：展示如何将AI生成的Markdown内容通过模板系统转换为Word文档
#
# 使用场景：
# 1. AI生成Markdown内容（使用Claude、GPT等）
# 2. 自动应用模板转换为HTML
# 3. 自动转换为DOCX
#
# 作者：Claude Code
# 版本：v1.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
${GREEN}AI集成工作流示例脚本${NC}

${YELLOW}使用方法：${NC}
  $0 [选项] <命令>

${YELLOW}命令：${NC}
  demo          运行完整演示流程
  generate      仅生成AI内容（需要API密钥）
  convert       仅转换已有Markdown
  clean         清理临时文件

${YELLOW}选项：${NC}
  -t, --template <模板>    指定模板 (academic|business|technical|simple)
  -o, --output <目录>      输出目录（默认: ai_workflow_output）
  --no-docx              不自动转换为DOCX
  --keep-html            保留HTML中间文件

${YELLOW}示例：${NC}
  # 运行完整演示
  $0 demo

  # 使用商务模板生成报告
  $0 demo --template business

  # 仅转换现有文件
  $0 convert --template technical -i my_doc.md

${YELLOW}环境变量：${NC}
  DEEPSEEK_API_KEY       DeepSeek API密钥（用于AI生成）

EOF
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi

    # 检查LibreOffice（如果需要DOCX转换）
    if [[ "$AUTO_DOCX" == "true" ]]; then
        if ! command -v soffice &> /dev/null; then
            print_warning "LibreOffice未安装，将跳过DOCX转换"
            AUTO_DOCX=false
        fi
    fi

    print_success "依赖检查完成"
}

# 创建输出目录
setup_output_dir() {
    OUTPUT_DIR="${OUTPUT_DIR:-ai_workflow_output}"
    mkdir -p "$OUTPUT_DIR"
    print_info "输出目录: $OUTPUT_DIR"
}

# AI生成Markdown内容
ai_generate_markdown() {
    local topic="${1:-技术发展趋势报告}"
    local template="${2:-technical}"
    local output_file="$OUTPUT_DIR/ai_generated.md"

    print_info "AI正在生成Markdown内容..."
    print_info "主题: $topic"
    print_info "模板: $template"

    # 检查API密钥
    if [[ -z "$DEEPSEEK_API_KEY" ]]; then
        print_warning "未设置DEEPSEEK_API_KEY环境变量"
        print_info "使用预生成的示例内容..."

        # 使用预生成的示例
        case "$template" in
            academic)
                cp "examples/academic_paper.md" "$output_file"
                ;;
            business)
                cp "examples/business_report.md" "$output_file"
                ;;
            technical)
                cp "examples/technical_doc.md" "$output_file"
                ;;
            simple)
                cp "examples/simple_letter.md" "$output_file"
                ;;
            *)
                cp "examples/technical_doc.md" "$output_file"
                ;;
        esac

        print_success "已使用示例内容: $output_file"
        return 0
    fi

    # 调用DeepSeek API生成内容
    print_info "正在调用DeepSeek API..."

    # 这里应该是实际的API调用代码
    # 示例代码（需要根据实际API调整）：
    #
    # curl -s https://api.deepseek.com/v1/chat/completions \
    #   -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
    #   -H "Content-Type: application/json" \
    #   -d '{
    #     "model": "deepseek-chat",
    #     "messages": [
    #       {"role": "system", "content": "你是一个专业的内容创作助手"},
    #       {"role": "user", "content": "请生成一篇关于'$topic'的Markdown文档"}
    #     ],
    #     "temperature": 0.7
    #   }' | jq -r '.choices[0].message.content' > "$output_file"

    print_warning "AI功能需要额外配置，当前使用示例内容"
    cp "examples/${template}_doc.md" "$output_file" 2>/dev/null || \
    cp "examples/technical_doc.md" "$output_file"

    print_success "Markdown内容已生成: $output_file"
}

# 应用模板转换
apply_template_convert() {
    local input_file="$1"
    local template="${2:-technical}"
    local html_file="${input_file%.md}.html"

    print_info "应用模板: $template"
    print_info "输入: $input_file"

    # 调用转换脚本
    python3 convert-md-to-html.py \
        "$input_file" \
        --template "$template" \
        -o "$OUTPUT_DIR" \
        > /dev/null 2>&1

    if [[ $? -eq 0 ]]; then
        print_success "HTML转换完成"
        HTML_FILE="$OUTPUT_DIR/$(basename ${input_file%.md}).html"
    else
        print_error "HTML转换失败"
        return 1
    fi
}

# 转换为DOCX
convert_to_docx() {
    local html_file="$1"
    local docx_file="${html_file%.html}.docx"

    print_info "正在转换为DOCX..."

    soffice --headless --convert-to docx \
        "$html_file" \
        --outdir "$OUTPUT_DIR" \
        > /dev/null 2>&1

    if [[ $? -eq 0 ]]; then
        print_success "DOCX文件已生成: $docx_file"
        DOCX_FILE="$docx_file"
    else
        print_warning "DOCX转换失败，请手动在Word中打开HTML文件"
    fi
}

# 完整工作流演示
run_demo() {
    print_info "开始AI集成工作流演示..."
    echo ""

    # 1. 检查依赖
    check_dependencies
    echo ""

    # 2. 设置输出目录
    setup_output_dir
    echo ""

    # 3. AI生成内容
    ai_generate_markdown "人工智能在医疗领域的应用" "$TEMPLATE"
    echo ""

    # 4. 应用模板转换
    apply_template_convert "$OUTPUT_DIR/ai_generated.md" "$TEMPLATE"
    echo ""

    # 5. 转换为DOCX
    if [[ "$AUTO_DOCX" == "true" ]]; then
        convert_to_docx "$HTML_FILE"
        echo ""
    fi

    # 6. 总结
    print_success "工作流完成！"
    echo ""
    echo "生成的文件："
    echo "  Markdown: $OUTPUT_DIR/ai_generated.md"
    if [[ -f "$HTML_FILE" ]] && [[ "$KEEP_HTML" == "true" ]]; then
        echo "  HTML:     $HTML_FILE"
    fi
    if [[ -n "$DOCX_FILE" ]] && [[ -f "$DOCX_FILE" ]]; then
        echo "  DOCX:     $DOCX_FILE"
    fi
    echo ""
    print_info "下一步：用Word打开生成的文件查看效果"
}

# 清理临时文件
clean_files() {
    print_info "清理临时文件..."

    if [[ -d "$OUTPUT_DIR" ]]; then
        rm -rf "$OUTPUT_DIR"
        print_success "已清理: $OUTPUT_DIR"
    else
        print_info "没有需要清理的文件"
    fi
}

# 主函数
main() {
    # 默认参数
    TEMPLATE="technical"
    OUTPUT_DIR=""
    AUTO_DOCX=true
    KEEP_HTML=false
    COMMAND=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--template)
                TEMPLATE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --no-docx)
                AUTO_DOCX=false
                shift
                ;;
            --keep-html)
                KEEP_HTML=true
                shift
                ;;
            demo|generate|convert|clean)
                COMMAND="$1"
                shift
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 如果没有指定命令，显示帮助
    if [[ -z "$COMMAND" ]]; then
        show_help
        exit 0
    fi

    # 执行命令
    case "$COMMAND" in
        demo)
            run_demo
            ;;
        generate)
            check_dependencies
            setup_output_dir
            ai_generate_markdown "" "$TEMPLATE"
            ;;
        convert)
            print_error "转换功能需要指定输入文件"
            print_info "示例: $0 convert -i document.md"
            ;;
        clean)
            clean_files
            ;;
    esac
}

# 运行主函数
main "$@"
