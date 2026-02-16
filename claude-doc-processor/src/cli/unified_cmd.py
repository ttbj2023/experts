#!/usr/bin/env python3
"""
统一文档转换命令

智能识别文档类型（PDF/DOCX）并选择最优处理流程
"""

import sys
import os
import argparse
import glob

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.converters.unified_converter import UnifiedConverter


def main():
    """统一文档转换命令行入口"""
    parser = argparse.ArgumentParser(
        description='智能文档转换器（自动识别PDF/DOCX并选择最优流程）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单个文件转换
  %(prog)s document.pdf
  %(prog)s document.docx -o output_dir

  # 批量转换
  %(prog)s docs/*.pdf
  %(prog)s documents/* -o batch_output

  # 自定义配置
  %(prog)s document.pdf --config custom.yaml
  %(prog)s document.docx --max-pages 10

支持的文档类型:
  PDF文档:
    • 数字版PDF → 直接提取文本（快速）
    • 扫描版PDF → 完整OCR流程

  DOCX文档:
    • 简单DOCX → 直接提取文本（快速）
    • 复杂DOCX → 完整处理流程
        """
    )

    # 必需参数
    parser.add_argument(
        'input_paths',
        nargs='+',  # 支持多个文件
        help='输入文档路径（支持通配符）'
    )

    # 可选参数
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='output',
        help='输出目录（默认: output）'
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
        help='最大处理页数（仅PDF，默认: 处理所有页）'
    )

    parser.add_argument(
        '--format-with-deepseek',
        action='store_true',
        dest='format_with_deepseek',
        help='启用DeepSeek排版优化（仅扫描版PDF）'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=200,
        help='PDF渲染DPI（仅扫描版PDF，默认: 200）'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='批量处理模式（为每个文件创建独立输出目录）'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
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

    # 展开通配符
    input_files = []
    for pattern in args.input_paths:
        matched_files = glob.glob(pattern)
        if matched_files:
            input_files.extend(matched_files)
        else:
            # 如果没有匹配到，可能是字面路径
            if os.path.exists(pattern):
                input_files.append(pattern)
            else:
                print(f"⚠️  警告: 未找到文件: {pattern}", file=sys.stderr)

    # 去重并排序
    input_files = sorted(set(input_files))

    if not input_files:
        print("❌ 错误: 没有找到有效的输入文件", file=sys.stderr)
        sys.exit(1)

    # 批量处理
    success_count = 0
    failed_count = 0
    results = []

    try:
        # 创建转换器
        converter = UnifiedConverter(config_path=args.config_path)

        # 应用环境变量覆盖
        if args.glm_api_key:
            converter.config['models']['glm']['api_key'] = args.glm_api_key
        if args.deepseek_api_key:
            converter.config['models']['deepseek']['api_key'] = args.deepseek_api_key

        # 处理每个文件
        for i, input_path in enumerate(input_files, 1):
            print(f"\n{'='*70}")
            print(f"处理文件 [{i}/{len(input_files)}]: {input_path}")
            print(f"{'='*70}\n")

            # 确定输出目录
            if args.batch:
                # 批量模式：为每个文件创建独立目录
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                file_output_dir = os.path.join(args.output_dir, base_name)
            else:
                # 非批量模式：所有文件输出到同一目录
                file_output_dir = args.output_dir

            try:
                # 执行转换
                success, output_path, stats = converter.convert(
                    input_path,
                    file_output_dir,
                    max_pages=args.max_pages,
                    format_with_deepseek=args.format_with_deepseek
                )

                # 记录结果
                if success:
                    success_count += 1
                    results.append({
                        'file': input_path,
                        'status': 'success',
                        'output': output_path,
                        'time': stats.get('processing_time', 0),
                        'method': stats.get('processing_method', 'unknown')
                    })
                else:
                    failed_count += 1
                    results.append({
                        'file': input_path,
                        'status': 'failed',
                        'error': stats.get('error', 'Unknown error')
                    })

            except KeyboardInterrupt:
                print("\n\n⚠️  用户中断", file=sys.stderr)
                break
            except Exception as e:
                failed_count += 1
                print(f"❌ 处理失败: {e}", file=sys.stderr)
                results.append({
                    'file': input_path,
                    'status': 'error',
                    'error': str(e)
                })

        # 输出总结
        print(f"\n{'='*70}")
        print("📊 批量处理总结")
        print(f"{'='*70}")
        print(f"总文件数: {len(input_files)}")
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {failed_count}")
        print(f"成功率: {success_count/len(input_files)*100:.1f}%")
        print(f"{'='*70}\n")

        # 详细结果
        if args.verbose and len(results) > 1:
            print("详细结果:")
            print("-" * 70)
            for r in results:
                if r['status'] == 'success':
                    print(f"✅ {os.path.basename(r['file'])}")
                    print(f"   方法: {r['method']}")
                    print(f"   时间: {r['time']:.2f}秒")
                    print(f"   输出: {r['output']}")
                else:
                    print(f"❌ {os.path.basename(r['file'])}")
                    print(f"   错误: {r.get('error', 'Unknown')}")
                print()

        sys.exit(0 if failed_count == 0 else 1)

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
