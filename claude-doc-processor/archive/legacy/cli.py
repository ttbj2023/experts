#!/usr/bin/env python3
"""
PDF → Word兼容HTML 转换工具 CLI
提供简洁的命令行接口
"""

import sys
import os
from pathlib import Path

# 将src目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import PDF2HTMLPipeline, parse_page_range


def print_banner():
    """打印横幅"""
    print("\n" + "=" * 70)
    print(" " * 15 + "PDF → Word兼容HTML 转换工具")
    print(" " * 10 + "基于「画框→识别→填空」三阶段流程")
    print("=" * 70 + "\n")


def print_usage():
    """打印使用说明"""
    print("""
使用方法:
  python cli.py <input.pdf> <output.html> [选项]

参数:
  input.pdf          输入PDF文件路径
  output.html        输出HTML文件路径

选项:
  -p, --page N       处理单个页面（指定页码）
  --pages RANGE      处理多个页面（格式: 1-10 或 1,3,5-7）
  --dpi N            PDF渲染DPI（默认: 200）
  --api-url URL      视觉模型API端点
                     默认: http://192.168.100.110:9999/v1/chat/completions
  --model NAME       视觉模型名称
                     默认: glm-4.6v-flash
  --keep-debug       保留中间调试文件
  --debug-dir DIR    调试文件目录

示例:
  # 处理整个PDF
  python cli.py input.pdf output.html

  # 处理单页（用于测试）
  python cli.py input.pdf output.html -p 12

  # 处理指定页码范围
  python cli.py input.pdf output.html --pages 1-10

  # 使用Qwen3VL模型
  python cli.py input.pdf output.html --model glm-4.6v-flash

  # 保留调试文件
  python cli.py input.pdf output.html --keep-debug

模型说明:
  - GLM-4.6V Flash: 需要LM Studio运行在端口9999
  - Qwen3VL 8B: 需要Ollama运行
  - 注意: 两个模型不能同时运行（显存限制）

技术支持:
  - 查看进度报告: DEVELOPMENT_PROGRESS.md
  - Word兼容规范: docs/HTML_support_by_WORD.md
    """)


def main():
    """CLI入口"""
    print_banner()

    # 检查参数
    if len(sys.argv) < 3:
        print("错误: 缺少必要参数\n")
        print_usage()
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_html = sys.argv[2]

    # 检查输入文件
    if not os.path.exists(input_pdf):
        print(f"错误: 输入文件不存在: {input_pdf}")
        sys.exit(1)

    # 解析选项
    pages = None
    dpi = 200
    api_url = "http://192.168.100.110:9999/v1/chat/completions"
    model = "glm-4.6v-flash"
    keep_debug = False
    debug_dir = None

    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg in ['-p', '--page']:
            if i + 1 >= len(sys.argv):
                print("错误: --page 需要页码参数")
                sys.exit(1)
            pages = [int(sys.argv[i + 1])]
            i += 2

        elif arg == '--pages':
            if i + 1 >= len(sys.argv):
                print("错误: --pages 需要页码范围参数")
                sys.exit(1)
            pages = parse_page_range(sys.argv[i + 1])
            i += 2

        elif arg == '--dpi':
            if i + 1 >= len(sys.argv):
                print("错误: --dpi 需要DPI值参数")
                sys.exit(1)
            dpi = int(sys.argv[i + 1])
            i += 2

        elif arg == '--api-url':
            if i + 1 >= len(sys.argv):
                print("错误: --api-url 需要URL参数")
                sys.exit(1)
            api_url = sys.argv[i + 1]
            i += 2

        elif arg == '--model':
            if i + 1 >= len(sys.argv):
                print("错误: --model 需要模型名称参数")
                sys.exit(1)
            model = sys.argv[i + 1]
            i += 2

        elif arg == '--keep-debug':
            keep_debug = True
            i += 1

        elif arg == '--debug-dir':
            if i + 1 >= len(sys.argv):
                print("错误: --debug-dir 需要目录参数")
                sys.exit(1)
            debug_dir = sys.argv[i + 1]
            i += 2

        else:
            print(f"错误: 未知选项 {arg}")
            print_usage()
            sys.exit(1)

    # 创建流水线
    pipeline = PDF2HTMLPipeline(
        vision_api_url=api_url,
        vision_api_key="sk-test-key",  # 本地模型通常不需要
        vision_model=model
    )

    # 执行转换
    success = pipeline.process_pdf_to_html(
        input_pdf=input_pdf,
        output_html=output_html,
        pages=pages,
        dpi=dpi,
        keep_intermediate=keep_debug,
        intermediate_dir=debug_dir
    )

    if success:
        print("\n✓ 转换完成!")
        print(f"\n使用Word打开生成的HTML文件: {output_html}")
        print("然后另存为DOCX格式即可编辑\n")
        sys.exit(0)
    else:
        print("\n✗ 转换失败\n")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
