#!/usr/bin/env python3
"""
统一文档转换命令（v4统一架构）

核心设计：
- DOCX只是PDF的前体（通过LibreOffice转换）
- PDF→MD是通用流程
- 根据PDF类型智能选择处理策略
- 支持逐页内容精修（Stage 3.5）
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
        description='统一文档转换器（v4架构：PDF/DOCX统一流程）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础转换
  %(prog)s document.pdf
  %(prog)s document.docx -o output_dir

  # 启用内容精修（Stage 3.5）
  %(prog)s document.pdf --refine-content

  # 限制页数
  %(prog)s document.pdf --max-pages 10

  # 从指定页开始处理
  %(prog)s document.pdf --start-page 51 --max-pages 50

  # 批量转换
  %(prog)s docs/*.pdf --batch
  %(prog)s documents/* -o batch_output

统一流程架构:
  Stage 0: DOCX→PDF预处理（可选）
  Stage 1: PDF类型检测（文档型 vs 扫描型）
  Stage 2: 图片提取（分支选择）
  Stage 3: OCR识别（Ollama + Qwen3 VL 逐页）
  Stage 3.5: 内容整理（DeepSeek逐页，可选）⭐
  Stage 4: 图片描述（Ollama + Qwen3 VL）
  Stage 5: 语义匹配（DeepSeek全局）
  Stage 6: 智能替换（去重+清理）

核心优势:
  - DOCX只是PDF的前体，统一处理流程
  - 智能检测PDF类型，自动选择最优策略
  - 支持逐页内容精修，提升输出质量
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
        '--start-page',
        type=int,
        default=1,
        dest='start_page',
        help='起始页码（从1开始，默认: 1）'
    )

    parser.add_argument(
        '--refine-content',
        action='store_true',
        dest='enable_content_refinement',
        help='启用Stage 3.5逐页内容整理（DeepSeek精修，推荐）'
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
        '--ollama-url',
        dest='ollama_url',
        help='Ollama API地址（覆盖配置文件）'
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
        if args.ollama_url:
            converter.config['models']['ollama']['api_url'] = args.ollama_url
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
                    start_page=args.start_page,
                    enable_content_refinement=args.enable_content_refinement
                )

                # 记录结果
                if success:
                    success_count += 1
                    results.append({
                        'file': input_path,
                        'status': 'success',
                        'output': output_path,
                        'time': stats.get('processing_time', 0),
                        'pdf_type': stats.get('pdf_type', 'unknown'),
                        'stages': stats.get('stages_completed', [])
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
                    print(f"   PDF类型: {r['pdf_type']}")
                    print(f"   处理时间: {r['time']:.2f}秒")
                    print(f"   完成阶段: {len(r['stages'])}个")
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
