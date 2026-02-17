"""
填空模块：HTML生成
基于模板库填充结构化内容，生成Word兼容的HTML文档
"""

import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from jinja2 import Template

import yaml

from utils import load_config


class HTMLGenerator:
    """HTML生成器"""

    # 禁用标签清单
    FORBIDDEN_TAGS = [
        '<section', '<article', '<header', '<footer', '<nav',
        '<figure', '<figcaption', '<video', '<audio', '<iframe',
        '<canvas', '<svg', '<template', '<form', '<input',
        '<select', '<button', '<textarea'
    ]

    # 禁用CSS属性清单
    FORBIDDEN_CSS = [
        'display: flex', 'display: grid', 'position: absolute',
        'position: fixed', 'border-radius', 'box-shadow',
        'transform', 'transition', 'opacity:', 'rgba(',
        'hsla(', 'linear-gradient', 'radial-gradient'
    ]

    def __init__(
        self,
        template_file: str = "templates/word_html_templates.yaml"
    ):
        """
        初始化HTML生成器

        Args:
            template_file: 模板文件路径
        """
        self.template_file = template_file
        self.templates = self._load_templates()
        self.global_css = self.templates.get('global_css_styles', '')
        self.html_skeleton = self.templates.get('global_html_skeleton', '')

    def _load_templates(self) -> Dict:
        """加载模板库"""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
            print(f"✓ 模板库加载成功: {self.template_file}")
            return template_data
        except Exception as e:
            print(f"✗ 模板库加载失败: {e}")
            return {}

    def generate_html(
        self,
        content_data: Dict,
        output_file: str,
        document_title: Optional[str] = None
    ) -> bool:
        """
        生成完整的HTML文档

        Args:
            content_data: 内容提取数据（page_content.json）
            output_file: 输出HTML文件路径
            document_title: 文档标题

        Returns:
            是否成功
        """
        print(f"\n生成HTML文档...")
        print("=" * 60)

        page_num = content_data['page_info']['page_number']

        try:
            # 1. 渲染所有元素
            print("  步骤1: 渲染元素...")
            element_htmls = self._render_elements(content_data['elements'])
            print(f"  成功: 渲染了 {len(element_htmls)} 个元素")

            # 2. 组装双栏布局
            print("  步骤2: 组装页面布局...")
            main_content = self._assemble_layout(
                element_htmls,
                content_data['elements'],
                content_data['layout_info']
            )
            print("  成功: 页面布局组装完成")

            # 3. 生成完整HTML
            print("  步骤3: 生成HTML文档...")
            full_html = self._generate_full_html(
                main_content=main_content,
                document_title=document_title or f"第{page_num}页",
                metadata=content_data
            )
            print("  成功: HTML文档生成完成")

            # 4. 合规性验证
            print("  步骤4: 合规性验证...")
            validation_result = self._validate_html(full_html)

            if not validation_result['passed']:
                print("  ⚠ 警告: 发现以下合规性问题:")
                for issue in validation_result['issues']:
                    print(f"    - {issue}")
            else:
                print("  ✓ 验证通过: HTML完全符合Word兼容规范")

            # 5. 保存文件
            print("  步骤5: 保存HTML文件...")
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            print(f"  ✓ 已保存: {output_file}")

            # 6. 生成验证报告
            report_file = output_file.replace('.html', '_validation_report.json')
            self._save_validation_report(validation_result, report_file)

            print("\n✓ HTML生成完成!")
            return True

        except Exception as e:
            print(f"\n✗ HTML生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _render_elements(self, elements: List[Dict]) -> List[str]:
        """
        渲染所有元素为HTML字符串

        Args:
            elements: 元素列表

        Returns:
            HTML字符串列表（按阅读顺序）
        """
        element_htmls = []

        for element in elements:
            elem_type = element['type']

            try:
                # 根据元素类型选择模板
                template_str = self.templates.get(elem_type, '')

                if not template_str:
                    print(f"  警告: 未找到类型 '{elem_type}' 的模板，使用默认段落模板")
                    template_str = self.templates.get('paragraph', '<p>{{ content }}</p>')

                # 创建Jinja2模板
                template = Template(template_str)

                # 准备模板变量
                template_vars = self._prepare_template_vars(element)

                # 渲染
                html = template.render(**template_vars)
                element_htmls.append(html)

            except Exception as e:
                print(f"  警告: 渲染元素 {element.get('element_id', 'unknown')} 失败: {e}")
                # 返回占位符
                element_htmls.append(f'<!-- 渲染失败: {element.get("element_id")} -->')

        return element_htmls

    def _prepare_template_vars(self, element: Dict) -> Dict:
        """
        准备模板变量

        Args:
            element: 元素数据

        Returns:
            模板变量字典
        """
        elem_type = element['type']
        layout_attr = element.get('layout_attr', {})

        vars = {
            'layout_attr': layout_attr,  # 提供完整的layout_attr字典
            'content': element.get('content', ''),
            'latex_code': element.get('latex_code', ''),
            'align': layout_attr.get('align', 'left'),
            'list_type': layout_attr.get('list_type', '1'),
            'start_num': layout_attr.get('start_num', 1),
            'border_width': '1',
            'cell_padding': '4',
            'has_header': layout_attr.get('has_header', False),
            'format': element.get('image_data', {}).get('format', 'PNG'),
            'base64_data': element.get('image_data', {}).get('base64_data', ''),
            'width': element.get('image_data', {}).get('width', 300),
            'height': element.get('image_data', {}).get('height', 200),
            'alt_text': element.get('image_data', {}).get('alt_text', '图片'),
            'caption_text': element.get('caption_text', ''),
        }

        # 列表数据
        if elem_type in ['ordered_list', 'unordered_list']:
            vars['list_items'] = element.get('list_items', [])

        # 表格数据
        if elem_type == 'table':
            table_data = element.get('table_data', {})
            vars['table_data'] = table_data
            vars['has_header'] = table_data.get('headers', []) != []
            vars['border_width'] = table_data.get('table_style', {}).get('border_width', '1')
            vars['cell_padding'] = table_data.get('table_style', {}).get('cell_padding', '4')

        return vars

    def _assemble_layout(
        self,
        element_htmls: List[str],
        elements: List[Dict],
        layout_info: Dict
    ) -> str:
        """
        组装页面布局（处理双栏等复杂布局）

        Args:
            element_htmls: 元素HTML字符串列表
            elements: 元素数据列表
            layout_info: 布局信息

        Returns:
            组装后的主内容HTML
        """
        column_count = layout_info.get('column_count', 1)

        # 单栏布局：直接拼接
        if column_count == 1:
            return '\n'.join(element_htmls)

        # 双栏布局
        # 策略：跨栏元素放外面，栏内元素用双栏容器包裹
        cross_column_elements = []
        left_column_elements = []
        right_column_elements = []

        for html, elem in zip(element_htmls, elements):
            layout_attr = elem.get('layout_attr', {})
            cross_column = layout_attr.get('cross_column', False)
            column = layout_attr.get('column', 'left')

            if cross_column:
                cross_column_elements.append(html)
            elif column == 'left':
                left_column_elements.append(html)
            elif column == 'right':
                right_column_elements.append(html)
            else:
                # 默认放入左栏
                left_column_elements.append(html)

        # 组装HTML
        parts = []

        # 跨栏元素
        if cross_column_elements:
            parts.extend(cross_column_elements)

        # 双栏容器
        if left_column_elements or right_column_elements:
            two_column_template = Template(self.templates.get('two_column_wrapper', '<div class="two-column">{{ column_content }}</div>'))

            # 合并左右栏内容（按阅读顺序）
            column_content = '\n'.join(left_column_elements + right_column_elements)

            two_column_html = two_column_template.render(column_content=column_content)
            parts.append(two_column_html)

        return '\n'.join(parts)

    def _generate_full_html(
        self,
        main_content: str,
        document_title: str,
        metadata: Dict
    ) -> str:
        """
        生成完整HTML文档

        Args:
            main_content: 主内容HTML
            document_title: 文档标题
            metadata: 元数据

        Returns:
            完整HTML文档
        """
        # 使用全局骨架模板
        skeleton_template = Template(self.html_skeleton)

        # 注入全局CSS
        full_html = skeleton_template.render(
            document_title=document_title,
            global_css=self.global_css,
            main_content=main_content
        )

        return full_html

    def _validate_html(self, html: str) -> Dict:
        """
        验证HTML合规性

        Args:
            html: HTML字符串

        Returns:
            验证结果
        """
        issues = []

        # 1. 检查禁用标签
        for tag in self.FORBIDDEN_TAGS:
            if tag in html:
                # 统计出现次数
                count = html.count(tag)
                issues.append(f"发现禁用标签: {tag} (出现{count}次)")

        # 2. 检查禁用CSS属性
        for css_prop in self.FORBIDDEN_CSS:
            if css_prop in html:
                count = html.count(css_prop)
                issues.append(f"发现禁用CSS属性: {css_prop} (出现{count}次)")

        # 3. 检查外部链接
        external_links = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', html)
        # 排除MathJax CDN（这是唯一允许的外部链接）
        external_links = [link for link in external_links if 'mathjax' not in link.lower()]
        if external_links:
            issues.append(f"发现外部链接: {len(external_links)}个（仅允许MathJax CDN）")

        # 4. 检查图片是否base64内嵌
        imgs = re.findall(r'<img[^>]*src=["\']([^"\']*)["\']', html)
        non_base64_imgs = [src for src in imgs if not src.startswith('data:image')]
        if non_base64_imgs:
            issues.append(f"发现非base64图片: {len(non_base64_imgs)}个")

        # 5. 检查公式标签格式
        formula_tags = re.findall(r'<script[^>]*type=["\']math/tex[^"\']*["\'][^>]*>(.*?)</script>', html, re.DOTALL)
        if formula_tags:
            print(f"  信息: 发现 {len(formula_tags)} 个公式标签")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'warnings': [],
            'stats': {
                'total_formulas': len(formula_tags),
                'total_images': len(imgs),
                'html_size': len(html)
            }
        }

    def _save_validation_report(self, validation_result: Dict, report_file: str):
        """保存验证报告"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'validation_result': validation_result
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"  ✓ 验证报告已保存: {report_file}")

    def generate_multi_page_html(
        self,
        content_data_list: List[Dict],
        output_file: str,
        document_title: str = "转换文档"
    ) -> bool:
        """
        生成多页HTML文档

        Args:
            content_data_list: 多页内容数据列表
            output_file: 输出文件路径
            document_title: 文档标题

        Returns:
            是否成功
        """
        print(f"\n生成多页HTML文档...")
        print("=" * 60)

        try:
            # 合并所有页面的主内容
            all_main_contents = []

            for idx, content_data in enumerate(content_data_list):
                print(f"  处理第 {idx + 1}/{len(content_data_list)} 页...")

                # 渲染元素
                element_htmls = self._render_elements(content_data['elements'])

                # 组装布局
                main_content = self._assemble_layout(
                    element_htmls,
                    content_data['elements'],
                    content_data['layout_info']
                )

                # 添加分页标记
                all_main_contents.append(f'<!-- 第{idx + 1}页 -->\n{main_content}')

            # 合并所有内容
            merged_content = '\n\n'.join(all_main_contents)

            # 生成完整HTML
            full_html = self._generate_full_html(
                main_content=merged_content,
                document_title=document_title,
                metadata={}
            )

            # 验证
            validation_result = self._validate_html(full_html)
            if not validation_result['passed']:
                print("  ⚠ 警告: 发现合规性问题:")
                for issue in validation_result['issues']:
                    print(f"    - {issue}")

            # 保存
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_html)

            print(f"  ✓ 多页HTML已保存: {output_file}")
            return True

        except Exception as e:
            print(f"  ✗ 多页HTML生成失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    print("填空模块测试")
    print("=" * 60)

    generator = HTMLGenerator()

    # 测试单页
    content_file = "output_content_test/page_content_0012.json"

    if os.path.exists(content_file):
        print(f"\n测试文件: {content_file}")
        content_data = load_json(content_file)

        if content_data:
            success = generator.generate_html(
                content_data=content_data,
                output_file="output_html_test/final_page_12.html",
                document_title="第12页测试"
            )

            if success:
                print("\n✓ 测试成功!")
            else:
                print("\n✗ 测试失败!")
    else:
        print(f"测试文件不存在: {content_file}")
        print("请先运行识别模块生成内容数据")
