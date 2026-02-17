"""
主流程集成：PDF→Word兼容HTML完整流水线
串联画框→识别→填空三个模块，实现自动化转换
"""

import os
import sys
import time
import argparse
from typing import Optional, List
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from layout_analyzer import LayoutAnalyzer
from content_extractor import ContentExtractor
from html_generator import HTMLGenerator


class PDF2HTMLPipeline:
    """PDF转HTML流水线"""

    def __init__(
        self,
        vision_api_url: str = "http://192.168.100.110:9999/v1/chat/completions",
        vision_api_key: str = "sk-test-key",
        vision_model: str = "glm-4.6v-flash",
        template_file: str = "templates/word_html_templates.yaml"
    ):
        """
        初始化流水线

        Args:
            vision_api_url: 视觉模型API端点
            vision_api_key: 视觉模型API密钥
            vision_model: 视觉模型名称
            template_file: HTML模板文件路径
        """
        self.vision_api_url = vision_api_url
        self.vision_api_key = vision_api_key
        self.vision_model = vision_model
        self.template_file = template_file

        # 初始化三个模块
        self.layout_analyzer = LayoutAnalyzer(
            api_url=vision_api_url,
            api_key=vision_api_key,
            model=vision_model
        )

        self.content_extractor = ContentExtractor(
            api_url=vision_api_url,
            api_key=vision_api_key,
            model=vision_model
        )

        self.html_generator = HTMLGenerator(
            template_file=template_file
        )

    def process_pdf_to_html(
        self,
        input_pdf: str,
        output_html: str,
        pages: Optional[List[int]] = None,
        dpi: int = 200,
        keep_intermediate: bool = False,
        intermediate_dir: Optional[str] = None
    ) -> bool:
        """
        处理PDF转换为HTML（完整流程）

        Args:
            input_pdf: 输入PDF文件路径
            output_html: 输出HTML文件路径
            pages: 要处理的页码列表（None表示全部）
            dpi: PDF渲染DPI
            keep_intermediate: 是否保留中间结果
            intermediate_dir: 中间结果目录

        Returns:
            是否成功
        """
        print("\n" + "=" * 80)
        print("PDF → Word兼容HTML 转换流水线")
        print("=" * 80)
        print(f"输入文件: {input_pdf}")
        print(f"输出文件: {output_html}")
        if pages:
            print(f"处理页码: {pages[0]}-{pages[-1]} (共{len(pages)}页)")
        else:
            print(f"处理页码: 全部")
        print(f"渲染DPI: {dpi}")
        print("=" * 80)

        # 准备中间结果目录
        if keep_intermediate:
            if intermediate_dir is None:
                intermediate_dir = Path(output_html).parent / "intermediate"
            intermediate_dir = Path(intermediate_dir)
            intermediate_dir.mkdir(parents=True, exist_ok=True)
            print(f"中间结果目录: {intermediate_dir}\n")
        else:
            intermediate_dir = None

        start_time = time.time()

        try:
            # 阶段1：画框（版面分析）
            print("\n【阶段1/3】画框：版面分析")
            print("-" * 80)
            layout_results = self.layout_analyzer.analyze_pdf(
                pdf_path=input_pdf,
                pages=pages,
                output_dir=str(intermediate_dir) if intermediate_dir else None,
                dpi=dpi
            )

            if not layout_results:
                print("✗ 错误: 版面分析失败")
                return False

            print(f"✓ 版面分析完成: 处理了 {len(layout_results)} 页")

            # 阶段2：识别（内容提取）
            print("\n【阶段2/3】识别：内容提取")
            print("-" * 80)
            content_results = []

            for idx, layout_data in enumerate(layout_results):
                page_num = layout_data['page_info']['page_number']
                print(f"\n处理第 {page_num} 页 ({idx + 1}/{len(layout_results)})...")

                content_data = self.content_extractor.extract_page_content(
                    layout_data=layout_data,
                    pdf_path=input_pdf,
                    output_dir=str(intermediate_dir) if intermediate_dir else None
                )

                if content_data:
                    content_results.append(content_data)
                    print(f"✓ 第 {page_num} 页内容提取成功")
                else:
                    print(f"✗ 第 {page_num} 页内容提取失败")
                    # 不中断流程，继续处理其他页

            if not content_results:
                print("✗ 错误: 所有页面内容提取失败")
                return False

            print(f"\n✓ 内容提取完成: 成功提取 {len(content_results)}/{len(layout_results)} 页")

            # 阶段3：填空（HTML生成）
            print("\n【阶段3/3】填空：HTML生成")
            print("-" * 80)

            if len(content_results) == 1:
                # 单页
                print("生成单页HTML...")
                success = self.html_generator.generate_html(
                    content_data=content_results[0],
                    output_file=output_html,
                    document_title=Path(input_pdf).stem
                )
            else:
                # 多页
                print(f"生成多页HTML（{len(content_results)}页）...")
                success = self.html_generator.generate_multi_page_html(
                    content_data_list=content_results,
                    output_file=output_html,
                    document_title=Path(input_pdf).stem
                )

            if not success:
                print("✗ 错误: HTML生成失败")
                return False

            # 统计信息
            elapsed_time = time.time() - start_time
            print("\n" + "=" * 80)
            print("✓ 转换成功!")
            print("=" * 80)
            print(f"输出文件: {output_html}")
            print(f"处理页数: {len(content_results)}")
            print(f"总耗时: {elapsed_time:.2f}秒")
            print(f"平均每页: {elapsed_time / len(content_results):.2f}秒")

            # 统计元素信息
            total_elements = sum(
                r['page_summary']['total_elements']
                for r in content_results
            )
            print(f"总元素数: {total_elements}")

            # 统计元素类型分布
            type_counts = {}
            for r in content_results:
                for elem_type, count in r['page_summary']['element_type_counts'].items():
                    type_counts[elem_type] = type_counts.get(elem_type, 0) + count

            print("元素类型分布:")
            for elem_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                print(f"  - {elem_type}: {count}")

            print("=" * 80)

            return True

        except KeyboardInterrupt:
            print("\n\n✗ 用户中断")
            return False

        except Exception as e:
            print(f"\n✗ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_single_page(
        self,
        input_pdf: str,
        page_num: int,
        output_html: str,
        dpi: int = 200,
        keep_intermediate: bool = True
    ) -> bool:
        """
        处理单个PDF页面（用于测试）

        Args:
            input_pdf: 输入PDF文件路径
            page_num: 页码（从1开始）
            output_html: 输出HTML文件路径
            dpi: PDF渲染DPI
            keep_intermediate: 是否保留中间结果

        Returns:
            是否成功
        """
        intermediate_dir = None
        if keep_intermediate:
            intermediate_dir = Path(output_html).parent / "intermediate"

        return self.process_pdf_to_html(
            input_pdf=input_pdf,
            output_html=output_html,
            pages=[page_num],
            dpi=dpi,
            keep_intermediate=keep_intermediate,
            intermediate_dir=str(intermediate_dir)
        )


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="PDF → Word兼容HTML 转换工具（画框→识别→填空）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 处理整个PDF
  python main.py input.pdf output.html

  # 处理单页（测试）
  python main.py input.pdf output.html --page 12

  # 处理指定页码范围
  python main.py input.pdf output.html --pages 1-10

  # 自定义DPI和模型
  python main.py input.pdf output.html --dpi 300 --model qwen3vl

  # 保留中间结果
  python main.py input.pdf output.html --keep-intermediate
        """
    )

    parser.add_argument(
        'input_pdf',
        help='输入PDF文件路径'
    )

    parser.add_argument(
        'output_html',
        help='输出HTML文件路径'
    )

    parser.add_argument(
        '--page', '-p',
        type=int,
        help='处理单个页面（指定页码）'
    )

    parser.add_argument(
        '--pages',
        help='处理多个页面（格式: 1-10 或 1,3,5-7）'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=200,
        help='PDF渲染DPI（默认: 200）'
    )

    parser.add_argument(
        '--vision-api-url',
        default='http://192.168.100.110:9999/v1/chat/completions',
        help='视觉模型API端点（默认: http://192.168.100.110:9999/v1/chat/completions）'
    )

    parser.add_argument(
        '--vision-api-key',
        default='sk-test-key',
        help='视觉模型API密钥（默认: sk-test-key）'
    )

    parser.add_argument(
        '--vision-model',
        default='glm-4.6v-flash',
        help='视觉模型名称（默认: glm-4.6v-flash）'
    )

    parser.add_argument(
        '--template-file',
        default='templates/word_html_templates.yaml',
        help='HTML模板文件路径'
    )

    parser.add_argument(
        '--keep-intermediate',
        action='store_true',
        help='保留中间结果（用于调试）'
    )

    parser.add_argument(
        '--intermediate-dir',
        help='中间结果目录（默认: 输出文件同目录下的intermediate/）'
    )

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input_pdf):
        print(f"错误: 输入文件不存在: {args.input_pdf}")
        sys.exit(1)

    # 解析页码
    pages = None
    if args.page:
        pages = [args.page]
    elif args.pages:
        pages = parse_page_range(args.pages)

    # 创建流水线
    pipeline = PDF2HTMLPipeline(
        vision_api_url=args.vision_api_url,
        vision_api_key=args.vision_api_key,
        vision_model=args.vision_model,
        template_file=args.template_file
    )

    # 执行转换
    success = pipeline.process_pdf_to_html(
        input_pdf=args.input_pdf,
        output_html=args.output_html,
        pages=pages,
        dpi=args.dpi,
        keep_intermediate=args.keep_intermediate,
        intermediate_dir=args.intermediate_dir
    )

    sys.exit(0 if success else 1)


def parse_page_range(page_range_str: str) -> List[int]:
    """
    解析页码范围字符串

    支持格式:
    - "1-10" -> [1,2,3,4,5,6,7,8,9,10]
    - "1,3,5-7" -> [1,3,5,6,7]
    """
    pages = []

    for part in page_range_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))

    return sorted(set(pages))


if __name__ == "__main__":
    main()
