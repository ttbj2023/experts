#!/usr/bin/env python3
"""
DOCX转Markdown转换命令

使用方法:
    python -m src.cli.docx_cmd input.docx -o output_dir
    python -m src.cli.docx_cmd input.docx --glm-api-key YOUR_KEY
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.converters.docx_converter import DOCXConverter


def main():
    """DOCX转Markdown命令行入口"""
    parser = argparse.ArgumentParser(
        description='DOCX转Markdown转换器（v3三阶段架构）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.docx -o output_dir
  %(prog)s input.docx -o output_dir --glm-api-key YOUR_KEY
  %(prog)s input.docx --config custom.yaml

处理流程:
  Stage 1: DOCX图片提取 + LibreOffice转换 + GLM识别
  Stage 2: GLM-4.6V-Flash图片描述
  Stage 3: DeepSeek语义匹配（全局上下文）
  Stage 4: 智能占位符替换
        """
    )

    # 必需参数
    parser.add_argument(
        'docx_path',
        help='DOCX文件路径'
    )

    # 可选参数
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='output_docx',
        help='输出目录（默认: output_docx）'
    )

    parser.add_argument(
        '--config',
        dest='config_path',
        help='配置文件路径（默认: config/default.yaml）'
    )

    # API密钥（覆盖配置）
    parser.add_argument(
        '--glm-api-key',
        dest='glm_api_key',
        help='GLM API密钥（覆盖配置文件）'
    )

    parser.add_argument(
        '--deepseek-key',
        dest='deepseek_api_key',
        help='DeepSeek API密钥（覆盖配置文件）'
    )

    parser.add_argument(
        '--glm-api-url',
        dest='glm_api_url',
        help='GLM API地址（覆盖配置文件）'
    )

    # LibreOffice选项
    parser.add_argument(
        '--libreoffice-timeout',
        type=int,
        dest='libreoffice_timeout',
        help='LibreOffice转换超时时间（秒）'
    )

    # 调试选项
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式（详细日志）'
    )

    # 解析参数
    args = parser.parse_args()

    # 验证输入文件
    if not os.path.exists(args.docx_path):
        print(f"❌ 错误: DOCX文件不存在: {args.docx_path}", file=sys.stderr)
        sys.exit(1)

    # 创建转换器
    try:
        converter = DOCXConverter(config_path=args.config_path)

        # 应用参数覆盖
        if args.glm_api_key:
            converter.config['glm_api_key'] = args.glm_api_key
        if args.deepseek_api_key:
            converter.config['models']['deepseek']['api_key'] = args.deepseek_api_key
        if args.glm_api_url:
            converter.config['models']['glm']['api_url'] = args.glm_api_url
        if args.libreoffice_timeout:
            converter.config['processing']['docx']['libreoffice_timeout'] = args.libreoffice_timeout
        if args.debug:
            converter.config['output']['log_level'] = 'DEBUG'

        # 执行转换
        print(f"\n{'='*70}")
        print(f"开始转换: {args.docx_path}")
        print(f"{'='*70}\n")

        success, output_path, stats = converter.convert(
            args.docx_path,
            args.output_dir
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
