#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转 Word 兼容 HTML 命令行接口
====================================

使用示例：
```bash
./convert-md-to-html.py document.md -o output/
./convert-md-to-html.py document.md --images-dir ./images
```

作者：Claude Code
版本：v1.0
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.converters.markdown_to_html_converter import MarkdownToHTMLConverter
from src.utils.template_loader import TemplateLoader, list_templates


def print_template_list():
    """打印可用模板列表"""
    templates = list_templates()

    if not templates:
        print("❌ 未找到可用模板")
        print(f"\n模板目录: config/templates/")
        return

    print("\n" + "=" * 70)
    print("可用模板列表")
    print("=" * 70)

    for template in templates:
        print(f"\n📄 {template['name']} - {template['display_name']}")
        print(f"   描述: {template['description']}")
        print(f"   版本: {template['version']}")

    print("\n" + "=" * 70)
    print("\n使用方法:")
    print("  ./convert-md-to-html.py document.md --template <模板名称> -o output/")
    print()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Markdown 转 Word 兼容 HTML 转换器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例：
  # 基础用法
  %(prog)s document.md -o output/

  # 使用模板
  %(prog)s document.md --template academic -o output/
  %(prog)s document.md --template business -o output/

  # 查看所有可用模板
  %(prog)s --list-templates

  # 指定图片目录
  %(prog)s document.md -o output/ --images-dir ./images

  # 使用自定义配置
  %(prog)s document.md --config config/custom.yaml

  # 自动转换为DOCX
  %(prog)s document.md --template academic --to-docx

  # 调试模式（详细日志）
  %(prog)s document.md --debug

输出文件：
  - output/document.html    # Word 兼容的 HTML 文件

模板系统：
  --template academic       # 学术论文模板（Times New Roman，严格格式）
  --template business       # 商务报告模板（专业配色，清晰层级）
  --template technical      # 技术文档模板（代码友好，深色主题）
  --template simple         # 普通文档模板（简洁清晰，标准排版）

后续操作：
  1. 用 Microsoft Word 打开生成的 HTML 文件
  2. 检查排版、公式、图片是否正常
  3. 文件 → 另存为 → 选择 .docx 格式
  4. 完成！DOCX 文件可直接编辑
        '''
    )

    # 必需参数（使用nargs='?'使其可选）
    parser.add_argument(
        'md_path',
        nargs='?',  # 可选参数
        help='输入 Markdown 文件路径'
    )

    # 可选参数
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default='output_md2html',
        help='输出目录（默认: output_md2html）'
    )

    parser.add_argument(
        '--images-dir',
        dest='images_dir',
        help='图片文件夹路径（默认: 输出目录/images/）'
    )

    parser.add_argument(
        '--config',
        dest='config_path',
        help='配置文件路径（默认: config/default.yaml）'
    )

    parser.add_argument(
        '--template',
        dest='template_name',
        help='使用指定模板（academic | business | technical | simple）'
    )

    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='列出所有可用模板'
    )

    parser.add_argument(
        '--to-docx',
        action='store_true',
        help='自动转换为DOCX格式（需要LibreOffice）'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式（详细日志）'
    )

    args = parser.parse_args()

    # 处理 --list-templates 参数
    if args.list_templates:
        print_template_list()
        sys.exit(0)

    # 如果没有提供输入文件，且不是 --list-templates，显示帮助
    if not hasattr(args, 'md_path'):
        parser.print_help()
        sys.exit(1)

    # 验证输入文件
    if not os.path.exists(args.md_path):
        print(f"❌ 错误: 文件不存在: {args.md_path}", file=sys.stderr)
        sys.exit(1)

    if not args.md_path.endswith(('.md', '.markdown')):
        print(f"⚠️  警告: 文件扩展名不是 .md，可能不是 Markdown 文件")

    # 创建转换器
    try:
        # 如果指定了模板，加载模板配置
        if args.template_name:
            template_loader = TemplateLoader()
            template_info = template_loader.get_template_info(args.template_name)

            if template_info is None:
                print(f"❌ 错误: 模板 '{args.template_name}' 不存在", file=sys.stderr)
                print(f"\n可用的模板:", file=sys.stderr)
                templates = list_templates()
                for t in templates:
                    print(f"  - {t['name']}: {t['display_name']}", file=sys.stderr)
                sys.exit(1)

            print(f"✓ 使用模板: {template_info['display_name']} (v{template_info['version']})")

        converter = MarkdownToHTMLConverter(
            config_path=args.config_path,
            template_name=args.template_name
        )

        # 设置调试模式
        if args.debug:
            import logging
            converter.logger.setLevel(logging.DEBUG)

        # 执行转换
        print(f"\n{'=' * 70}")
        print("Markdown 转 Word 兼容 HTML")
        print(f"{'=' * 70}\n")

        success, output_path, stats = converter.convert(
            args.md_path,
            args.output_dir,
            images_dir=args.images_dir
        )

        if success:
            print(f"\n✅ 转换成功！")
            print(f"\n输出文件: {output_path}")

            # 如果需要自动转换为DOCX
            if args.to_docx:
                print(f"\n正在转换为DOCX...")

                # 检查LibreOffice是否可用
                import subprocess
                try:
                    result = subprocess.run(
                        ['soffice', '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if result.returncode == 0:
                        # 执行转换
                        docx_output = args.output_dir
                        result = subprocess.run([
                            'soffice',
                            '--headless',
                            '--convert-to', 'docx',
                            output_path,
                            '--outdir', docx_output
                        ], capture_output=True, text=True, timeout=60)

                        if result.returncode == 0:
                            # 获取DOCX文件路径
                            docx_path = output_path.replace('.html', '.docx')
                            print(f"✅ DOCX文件已生成: {docx_path}")
                        else:
                            print(f"⚠️  DOCX转换失败: {result.stderr}")
                    else:
                        print(f"⚠️  未检测到LibreOffice，无法自动转换为DOCX")
                        print(f"   请安装LibreOffice或手动在Word中打开HTML文件另存为DOCX")

                except FileNotFoundError:
                    print(f"⚠️  未检测到LibreOffice，无法自动转换为DOCX")
                    print(f"   请安装LibreOffice或手动在Word中打开HTML文件另存为DOCX")
                except Exception as e:
                    print(f"⚠️  DOCX转换出错: {e}")

            print(f"\n下一步操作:")
            print(f"  1. 用 Microsoft Word 打开: {output_path}")
            if not args.to_docx:
                print(f"  2. 检查排版、公式、图片是否正常")
                print(f"  3. 文件 → 另存为 → 选择 .docx 格式")
            print(f"  4. 完成！DOCX 文件可直接编辑\n")
            sys.exit(0)
        else:
            error_msg = stats.get('error', '未知错误')
            print(f"\n❌ 转换失败: {error_msg}\n", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}\n", file=sys.stderr)
        import traceback
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
