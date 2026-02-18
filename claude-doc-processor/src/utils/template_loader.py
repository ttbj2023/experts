#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板加载器
=========

加载和管理文档样式模板，支持多种文档类型的预置模板和自定义模板。

功能：
- 从YAML文件加载模板配置
- 提供模板信息查询
- 合并模板配置到默认配置
- 验证模板有效性

作者：Claude Code
版本：v1.0
"""

import os
import yaml
from typing import Dict, Optional, List
from pathlib import Path


class TemplateLoader:
    """模板加载器"""

    def __init__(self, templates_dir: str = None):
        """
        初始化模板加载器

        Args:
            templates_dir: 模板目录路径（默认: config/templates/）
        """
        if templates_dir is None:
            # 默认模板目录
            project_root = Path(__file__).parent.parent.parent
            templates_dir = project_root / 'config' / 'templates'

        self.templates_dir = Path(templates_dir)
        self._template_cache = {}

    def list_templates(self) -> List[Dict[str, str]]:
        """
        列出所有可用模板

        Returns:
            模板列表，每个模板包含 name, description, file 等信息
        """
        templates = []

        if not self.templates_dir.exists():
            return templates

        # 遍历模板目录
        for template_file in self.templates_dir.glob('*.yaml'):
            # 跳过示例文件
            if template_file.name.startswith('custom_'):
                continue

            # 读取模板信息
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_config = yaml.safe_load(f)

                if template_config and 'template_name' in template_config:
                    templates.append({
                        'name': template_file.stem,
                        'display_name': template_config.get('template_name', template_file.stem),
                        'description': template_config.get('template_description', ''),
                        'version': template_config.get('template_version', '1.0.0'),
                        'file': str(template_file)
                    })
            except Exception as e:
                # 跳过无法解析的文件
                continue

        # 按名称排序
        templates.sort(key=lambda x: x['name'])

        return templates

    def load_template(self, template_name: str) -> Optional[Dict]:
        """
        加载指定模板

        Args:
            template_name: 模板名称（不含.yaml扩展名）

        Returns:
            模板配置字典，如果模板不存在则返回None
        """
        # 检查缓存
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        # 构建模板文件路径
        template_file = self.templates_dir / f'{template_name}.yaml'

        if not template_file.exists():
            return None

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_config = yaml.safe_load(f)

            # 缓存模板配置
            self._template_cache[template_name] = template_config

            return template_config

        except Exception as e:
            raise ValueError(f"无法加载模板 '{template_name}': {e}")

    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """
        获取模板基本信息

        Args:
            template_name: 模板名称

        Returns:
            模板信息字典，包含 name, description, version 等
        """
        template_config = self.load_template(template_name)

        if template_config is None:
            return None

        return {
            'name': template_name,
            'display_name': template_config.get('template_name', template_name),
            'description': template_config.get('template_description', ''),
            'version': template_config.get('template_version', '1.0.0'),
            'author': template_config.get('template_author', '')
        }

    def merge_template_config(
        self,
        base_config: Dict,
        template_name: str
    ) -> Dict:
        """
        将模板配置合并到基础配置中

        Args:
            base_config: 基础配置字典
            template_name: 模板名称

        Returns:
            合并后的配置字典
        """
        template_config = self.load_template(template_name)

        if template_config is None:
            raise ValueError(f"模板 '{template_name}' 不存在")

        # 深度合并配置
        merged_config = self._deep_merge(base_config, template_config)

        return merged_config

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """
        深度合并两个字典

        Args:
            base: 基础字典
            override: 覆盖字典

        Returns:
            合并后的字典
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 递归合并嵌套字典
                result[key] = self._deep_merge(result[key], value)
            else:
                # 直接覆盖
                result[key] = value

        return result

    def validate_template(self, template_name: str) -> tuple[bool, str]:
        """
        验证模板是否有效

        Args:
            template_name: 模板名称

        Returns:
            (是否有效, 错误信息)
        """
        try:
            template_config = self.load_template(template_name)

            if template_config is None:
                return False, f"模板 '{template_name}' 不存在"

            # 检查必需字段
            required_fields = ['template_name', 'template_version']
            for field in required_fields:
                if field not in template_config:
                    return False, f"模板缺少必需字段: {field}"

            # 检查样式配置
            if 'styles' not in template_config:
                return False, "模板缺少 styles 配置"

            # 检查字体配置
            styles = template_config.get('styles', {})
            if 'fonts' not in styles:
                return False, "模板缺少字体配置"

            return True, ""

        except Exception as e:
            return False, f"验证模板时出错: {e}"

    def get_template_config_for_html_generator(
        self,
        template_name: str
    ) -> Dict:
        """
        获取适用于HTML生成器的模板配置

        将模板配置转换为HTML生成器可用的格式。

        Args:
            template_name: 模板名称

        Returns:
            HTML生成器配置字典
        """
        template_config = self.load_template(template_name)

        if template_config is None:
            raise ValueError(f"模板 '{template_name}' 不存在")

        # 提取样式配置
        styles = template_config.get('styles', {})
        layout = template_config.get('layout', {})
        headings = template_config.get('headings', {})
        tables = template_config.get('tables', {})
        images = template_config.get('images', {})
        formulas = template_config.get('formulas', {})
        lists = template_config.get('lists', {})
        code_blocks = template_config.get('code_blocks', {})
        blockquotes = template_config.get('blockquotes', {})
        features = template_config.get('features', {})

        # 获取间距配置
        spacing = styles.get('spacing', {})

        # 构建HTML生成器配置
        html_config = {
            'template_name': template_name,

            # ========== 字体配置 ==========
            'default_font': styles.get('fonts', {}).get('default', '宋体'),
            'western_font': styles.get('fonts', {}).get('western', 'Times New Roman'),
            'heading_font': styles.get('fonts', {}).get('heading', '黑体'),
            'code_font': styles.get('fonts', {}).get('code', 'Courier New'),

            # ========== 字号配置 ==========
            'default_font_size': styles.get('font_sizes', {}).get('body', 12),
            'heading1_size': headings.get('h1', {}).get('font_size', styles.get('font_sizes', {}).get('heading1', 18)),
            'heading2_size': headings.get('h2', {}).get('font_size', styles.get('font_sizes', {}).get('heading2', 16)),
            'heading3_size': headings.get('h3', {}).get('font_size', styles.get('font_sizes', {}).get('heading3', 14)),
            'heading4_size': headings.get('h4', {}).get('font_size', styles.get('font_sizes', {}).get('heading4', 12)),
            'heading5_size': headings.get('h5', {}).get('font_size', styles.get('font_sizes', {}).get('heading5', 12)),
            'heading6_size': headings.get('h6', {}).get('font_size', styles.get('font_sizes', {}).get('heading6', 12)),

            # ========== 颜色配置 ==========
            'text_color': styles.get('colors', {}).get('text', '#000000'),
            'heading_color': styles.get('colors', {}).get('heading', '#000000'),
            'link_color': styles.get('colors', {}).get('link', '#0000FF'),

            # ========== 行距配置 ==========
            'line_height': spacing.get('line_height', 1.5),

            # ========== 段落间距配置 ==========
            'paragraph_spacing_before': spacing.get('paragraph_spacing_before', 0),
            'paragraph_spacing_after': spacing.get('paragraph_spacing_after', 12),
            'paragraph_first_line_indent': layout.get('paragraph', {}).get('first_line_indent', '2em'),
            'paragraph_text_align': layout.get('paragraph', {}).get('text_align', 'justify'),

            # ========== 标题间距和分页配置 ==========
            'heading1_align': headings.get('h1', {}).get('text_align', 'center'),
            'heading1_margin_top': headings.get('h1', {}).get('margin_top', 24),
            'heading1_margin_bottom': headings.get('h1', {}).get('margin_bottom', 18),
            'heading1_page_break_before': headings.get('h1', {}).get('page_break_before', False),

            'heading2_align': headings.get('h2', {}).get('text_align', 'left'),
            'heading2_margin_top': headings.get('h2', {}).get('margin_top', 18),
            'heading2_margin_bottom': headings.get('h2', {}).get('margin_bottom', 12),
            'heading2_page_break_before': headings.get('h2', {}).get('page_break_before', False),

            'heading3_align': headings.get('h3', {}).get('text_align', 'left'),
            'heading3_margin_top': headings.get('h3', {}).get('margin_top', 14),
            'heading3_margin_bottom': headings.get('h3', {}).get('margin_bottom', 6),

            'heading4_align': headings.get('h4', {}).get('text_align', 'left'),
            'heading4_margin_top': headings.get('h4', {}).get('margin_top', 12),
            'heading4_margin_bottom': headings.get('h4', {}).get('margin_bottom', 6),

            # ========== 页面边距配置 ==========
            'page_size': layout.get('page_size', 'A4'),
            'page_margin_top': layout.get('margins', {}).get('top', '2.54cm'),
            'page_margin_bottom': layout.get('margins', {}).get('bottom', '2.54cm'),
            'page_margin_left': layout.get('margins', {}).get('left', '3.17cm'),
            'page_margin_right': layout.get('margins', {}).get('right', '3.17cm'),

            # ========== 表格样式配置 ==========
            'table_border_color': tables.get('border_color', '#000000'),
            'table_border_width': f"{tables.get('border_width', 0.5)}pt",
            'table_cell_padding': f"{tables.get('cell_padding', 4)}pt",
            'table_header_bg': tables.get('header_row', {}).get('background_color', '#F0F0F0'),

            # ========== 代码块样式配置 ==========
            'code_background_color': code_blocks.get('background_color', '#F5F5F5'),
            'code_padding': f"{code_blocks.get('padding', 10)}pt",

            # ========== 图片配置 ==========
            'image_embedding': images.get('embedding', 'base64'),
            'image_max_size': images.get('max_dimension', 1920),
            'image_quality': images.get('quality', 90),

            # ========== 公式配置 ==========
            'formula_format': formulas.get('format', 'script'),

            # ========== 标书特殊配置 ==========
            'table_content_font_size': styles.get('font_sizes', {}).get('table_content', 10.5),
            'fixed_line_spacing': spacing.get('fixed_line_spacing', 22),

            # ========== 法定声明配置 ==========
            'legal_font_family': template_config.get('advanced', {}).get('tender_elements', {}).get('legal_statement', {}).get('font_family', '仿宋_GB2312'),
            'legal_font_size': template_config.get('advanced', {}).get('tender_elements', {}).get('legal_statement', {}).get('font_size', 14),

            # ========== 功能开关 ==========
            'enable_columns': features.get('enable_columns', False),
            'enable_tables': features.get('enable_tables', True),
            'enable_lists': features.get('enable_lists', True),
        }

        return html_config


# 便捷函数
def load_template(template_name: str, templates_dir: str = None) -> Optional[Dict]:
    """
    加载模板的便捷函数

    Args:
        template_name: 模板名称
        templates_dir: 模板目录路径（可选）

    Returns:
        模板配置字典
    """
    loader = TemplateLoader(templates_dir)
    return loader.load_template(template_name)


def list_templates(templates_dir: str = None) -> List[Dict]:
    """
    列出所有模板的便捷函数

    Args:
        templates_dir: 模板目录路径（可选）

    Returns:
        模板列表
    """
    loader = TemplateLoader(templates_dir)
    return loader.list_templates()
