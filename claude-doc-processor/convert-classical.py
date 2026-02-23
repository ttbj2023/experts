#!/usr/bin/env python3
"""
古典文献转换器 - 专用入口

专门处理古籍、家谱等古典中文文献

使用方法:
    # 通用古籍
    ./convert-classical.py document.pdf

    # 家谱（深度优化）
    ./convert-classical.py genealogy.pdf --genealogy

    # 经典文献
    ./convert-classical.py classic.pdf --classic

    # 输出图片+文字
    ./convert-classical.py document.pdf --embed-images
"""

import sys
import os
import argparse

# 添加src到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """古典文献转换命令行入口"""
    parser = argparse.ArgumentParser(
        description='古典文献转换器（古籍、家谱专用）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 通用古籍
  %(prog)s document.pdf

  # 家谱处理（推荐）
  %(prog)s genealogy.pdf --genealogy --embed-images

  # 批量处理家谱
  %(prog)s genealogy/*.pdf --genealogy --batch

古典文献处理特点:
  - 保留繁体字和竖排格式
  - 识别世系表和家族关系
  - 嵌入原始扫描图片
  - 提取人名、地名、日期
  - 支持家谱术语（承祧、嗣、配等）

配置:
  --classical: 通用古籍模式
  --genealogy: 家谱模式（深度优化）
  --classic: 经典文献模式
        """
    )

    # 输入文件
    parser.add_argument(
        'input_files',
        nargs='+',
        help='输入文件（PDF/DOCX）'
    )

    # 输出目录
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        help='输出目录（默认：output/classical/）'
    )

    # 文献类型
    doc_type_group = parser.add_mutually_exclusive_group()
    doc_type_group.add_argument(
        '--classical',
        action='store_const',
        const='classical',
        dest='doc_type',
        help='通用古籍模式'
    )
    doc_type_group.add_argument(
        '--genealogy',
        action='store_const',
        const='genealogy',
        dest='doc_type',
        help='家谱模式（推荐）'
    )
    doc_type_group.add_argument(
        '--classic',
        action='store_const',
        const='classic',
        dest='doc_type',
        help='经典文献模式'
    )

    # 处理选项
    parser.add_argument(
        '--max-pages',
        type=int,
        help='最大处理页数'
    )
    parser.add_argument(
        '--start-page',
        type=int,
        default=1,
        help='起始页码（从1开始）'
    )
    parser.add_argument(
        '--embed-images',
        action='store_true',
        help='嵌入原始扫描图片（推荐）'
    )
    parser.add_argument(
        '--refine-content',
        action='store_true',
        help='启用内容整理（Stage 3.5）'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='批量处理模式'
    )

    # Ollama 配置
    parser.add_argument(
        '--ollama-url',
        dest='ollama_url',
        help='Ollama API地址'
    )
    parser.add_argument(
        '--model',
        dest='model_name',
        help='Ollama 模型名称（默认：qwen3-vl:8b）'
    )

    # 解析参数
    args = parser.parse_args()

    # 导入转换器
    from src.converters.classical_converter import ClassicalConverter
    import glob

    # 展开通配符
    input_files = []
    for pattern in args.input_files:
        matches = glob.glob(pattern)
        if matches:
            input_files.extend(matches)
        else:
            input_files.append(pattern)

    # 确定输出目录
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = 'output/classical/'

    # 确定文献类型
    doc_type = args.doc_type or 'classical'

    # 创建转换器
    converter = ClassicalConverter(doc_type=doc_type)

    # 应用 Ollama 配置
    if args.ollama_url:
        converter.config['models']['ollama']['api_url'] = args.ollama_url
    if args.model_name:
        converter.config['models']['ollama']['vision_model'] = args.model_name
        converter.config['models']['ollama']['text_model'] = args.model_name

    # 处理文件
    success_count = 0
    failed_count = 0

    for i, input_path in enumerate(input_files, 1):
        print(f"\n{'='*70}")
        print(f"处理文件 [{i}/{len(input_files)}]: {input_path}")
        print(f"{'='*70}\n")
        print(f"文献类型: {doc_type}")

        try:
            success, output_file, stats = converter.convert(
                input_path=input_path,
                output_dir=output_dir,
                max_pages=args.max_pages,
                start_page=args.start_page,
                enable_content_refinement=args.refine_content
            )

            if success:
                success_count += 1
                print(f"\n✅ 成功: {output_file}")
            else:
                failed_count += 1
                print(f"\n❌ 失败")

        except Exception as e:
            failed_count += 1
            print(f"\n❌ 异常: {e}")

    # 输出总结
    print(f"\n{'='*70}")
    print("处理总结")
    print(f"{'='*70}")
    print(f"总计: {len(input_files)} 个文件")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"成功率: {success_count/len(input_files)*100:.1f}%")
    print(f"{'='*70}\n")

    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
