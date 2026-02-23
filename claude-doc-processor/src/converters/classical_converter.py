#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古典文献转换器

专门处理古籍、家谱等古典中文文献
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

from .unified_converter import UnifiedConverter


logger = logging.getLogger(__name__)


class ClassicalConverter(UnifiedConverter):
    """
    古典文献转换器

    继承自 UnifiedConverter，专门优化古典中文文献处理
    """

    # 文献类型
    DOC_TYPE_GENERAL = "general"        # 通用古籍
    DOC_TYPE_GENEALOGY = "genealogy"    # 家谱
    DOC_TYPE_CLASSIC = "classic"        # 经典文献

    def __init__(self, config_path: str = None, doc_type: str = DOC_TYPE_GENERAL):
        """
        初始化古典文献转换器

        Args:
            config_path: 配置文件路径
            doc_type: 文献类型 (general/genealogy/classic)
        """
        # 加载古典文献配置
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / 'config' / 'classical_chinese.yaml'

        super().__init__(config_path)

        self.doc_type = doc_type
        self.classical_config = self.config.get('processing', {}).get('classical', {})
        self.genealogy_config = self.config.get('processing', {}).get('genealogy', {})

        logger.info(f"初始化古典文献转换器: 类型={doc_type}")

    def convert(
        self,
        input_path: str,
        output_dir: str,
        max_pages: int = None,
        start_page: int = 1,
        enable_content_refinement: bool = None
    ) -> Tuple[bool, str, Dict]:
        """
        转换古典文献

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            max_pages: 最大处理页数
            start_page: 起始页码
            enable_content_refinement: 是否启用内容整理

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self._start_timer()

        logger.info("="*60)
        logger.info("古典文献处理模式")
        logger.info("="*60)
        logger.info(f"文献类型: {self.doc_type}")
        logger.info(f"输入文件: {input_path}")

        # 使用古典文献专用的 OCR 方法
        # 临时覆盖 vision_client 的方法
        original_ocr_method = self.vision_client.ocr_page
        self.vision_client.ocr_page = lambda img_path: self.vision_client.ocr_classical_page(
            img_path, doc_type=self.doc_type
        )

        try:
            # 调用父类转换方法
            success, output_file, stats = super().convert(
                input_path=input_path,
                output_dir=output_dir,
                max_pages=max_pages,
                start_page=start_page,
                enable_content_refinement=enable_content_refinement
            )

            # 后处理：古典文献特定优化
            if success and output_file:
                self._post_process_classical(output_file)

            return success, output_file, stats

        finally:
            # 恢复原方法
            self.vision_client.ocr_page = original_ocr_method

    def _post_process_classical(self, output_file: str):
        """
        后处理：优化古典文献输出

        Args:
            output_file: 输出文件路径
        """
        logger.info("")
        logger.info("="*60)
        logger.info("古典文献后处理")
        logger.info("="*60)

        # 读取输出
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 应用后处理规则
        content = self._fix_traditional_chinese(content)
        content = self._restore_punctuation(content)
        content = self._format_lineage_table(content)

        # 保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info("✅ 后处理完成")

    def _fix_traditional_chinese(self, content: str) -> str:
        """
        修复繁体字识别问题

        Args:
            content: 原始内容

        Returns:
            修复后的内容
        """
        # 这里可以添加繁简转换、异体字统一等处理
        # 暂时保持原样
        return content

    def _restore_punctuation(self, content: str) -> str:
        """
        恢复古标点符号

        Args:
            content: 原始内容

        Returns:
            恢复后的内容
        """
        # 这里可以添加标点符号修复逻辑
        # 例如：将现代标点转换为古标点
        return content

    def _format_lineage_table(self, content: str) -> str:
        """
        格式化世系表（家谱专用）

        Args:
            content: 原始内容

        Returns:
            格式化后的内容
        """
        if self.doc_type != self.DOC_TYPE_GENEALOGY:
            return content

        # 提取世系信息并格式化为表格
        # 这里需要根据实际格式进行解析

        return content

    def _get_ocr_prompt(self, page_num: int) -> str:
        """
        获取 OCR 提示词（古典文献专用）

        Args:
            page_num: 页码

        Returns:
            OCR 提示词
        """
        if self.doc_type == self.DOC_TYPE_GENEALOGY:
            return self.config.get('prompts', {}).get('genealogy_ocr', '')
        else:
            return self.config.get('prompts', {}).get('classical_ocr', '')

    def _should_embed_image(self) -> bool:
        """
        判断是否应该嵌入原始图片

        Returns:
            是否嵌入图片
        """
        # 古典文献默认嵌入原始图片
        return True
