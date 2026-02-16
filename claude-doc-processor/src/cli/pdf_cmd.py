#!/usr/bin/env python3
"""
PDF转Markdown转换命令

使用方法:
    python -m src.cli.pdf_cmd input.pdf -o output_dir
    python -m src.cli.pdf_cmd input.pdf --max-pages 10 --format-with-deepseek
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.converters.pdf_converter import PDFConverter


def main():
    """PDF转Markdown命令行入口"""
    parser = argparse.ArgumentParser(
        description='PDF转Markdown转换器（完整版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.pdf -o output_dir
  %(prog)s input.pdf -o output_dir --max-pages 10
  %(prog)s input.pdf -o output_dir --format-with-deepseek
  %(prog)s input.pdf --config custom.yaml

处理流程:
  Stage 1: GLM-4.6V-Flash OCR + 图片占位符
  Stage 1.5: DeepSeek排版优化（可选）
  Stage 2: OpenCV精确图片提取
  Stage 3: GLM-4V图片描述
  Stage 4: DeepSeek语义匹配
  Stage 5: 占位符替换
        """
    )

    # 必需参数
    parser.add_argument(
        'pdf_path',
        help='PDF文件路径'
    )

    # 可选参数
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='output_pdf',
        help='输出目录（默认: output_pdf）'
    )

    parser.add_argument(
        '--config',
        dest='config_path',
        help='配置文件路径（默认: config/default.yaml）'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        dest='max_pages',
        help='最大处理页数（默认: 处理所有页）'
    )

    parser.add_argument(
        '--format-with-deepseek',
        action='store_true',
        dest='format_with_deepseek',
        help='启用DeepSeek排版优化（Stage 1.5）'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=200,
        help='PDF渲染DPI（默认: 200）'
    )

    # 环境变量覆盖（可选）
    parser.add_argument(
        '--glm-api-key',
        dest='glm_api_key',
        help='GLM API密钥（覆盖配置文件）'
    )

    parser.add_argument(
        '--deepseek-api-key',
        dest='deepseek_api_key',
        help='DeepSeek API密钥（覆盖配置文件）'
    )

    # 解析参数
    args = parser.parse_args()

    # 验证输入文件
    if not os.path.exists(args.pdf_path):
        print(f"❌ 错误: PDF文件不存在: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    # 创建转换器
    try:
        converter = PDFConverter(config_path=args.config_path)

        # 应用环境变量覆盖
        if args.glm_api_key:
            converter.config['glm_api_key'] = args.glm_api_key
        if args.deepseek_api_key:
            converter.config['models']['deepseek']['api_key'] = args.deepseek_api_key

        # 执行转换
        print(f"\n{'='*70}")
        print(f"开始转换: {args.pdf_path}")
        print(f"{'='*70}\n")

        success, output_path, stats = converter.convert(
            args.pdf_path,
            args.output_dir,
            max_pages=args.max_pages,
            format_with_deepseek=args.format_with_deepseek
        )

        # 输出结果
        print(f"\n{'='*70}")
        if success:
            print(f"✅ 转换成功!")
            print(f"{'='*70}")
            print(f"输出文件: {output_path}")
            print(f"处理时间: {stats.get('processing_time', 0):.2f} 秒")
            print(f"总图片数: {stats.get('total_images', 0)}")
            print(f"匹配成功: {stats.get('matched_images', 0)}")
            print(f"完成阶段: {len(stats.get('stages_completed', []))} 个")
            print(f"{'='*70}\n")
            sys.exit(0)
        else:
            error_msg = stats.get('error', 'Unknown error')
            print(f"❌ 转换失败: {error_msg}", file=sys.stderr)
            print(f"{'='*70}\n", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
