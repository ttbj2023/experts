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

  # 指定图片目录
  %(prog)s document.md -o output/ --images-dir ./images

  # 使用自定义配置
  %(prog)s document.md --config config/custom.yaml

  # 调试模式（详细日志）
  %(prog)s document.md --debug

输出文件：
  - output/document.html    # Word 兼容的 HTML 文件

后续操作：
  1. 用 Microsoft Word 打开生成的 HTML 文件
  2. 检查排版、公式、图片是否正常
  3. 文件 → 另存为 → 选择 .docx 格式
  4. 完成！DOCX 文件可直接编辑
        '''
    )

    # 必需参数
    parser.add_argument(
        'md_path',
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
        '--debug',
        action='store_true',
        help='启用调试模式（详细日志）'
    )

    args = parser.parse_args()

    # 验证输入文件
    if not os.path.exists(args.md_path):
        print(f"❌ 错误: 文件不存在: {args.md_path}", file=sys.stderr)
        sys.exit(1)

    if not args.md_path.endswith(('.md', '.markdown')):
        print(f"⚠️  警告: 文件扩展名不是 .md，可能不是 Markdown 文件")

    # 创建转换器
    try:
        converter = MarkdownToHTMLConverter(config_path=args.config_path)

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
            print(f"\n下一步操作:")
            print(f"  1. 用 Microsoft Word 打开: {output_path}")
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
