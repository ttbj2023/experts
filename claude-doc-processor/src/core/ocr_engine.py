"""
OCR 引擎

统一的OCR相关工具，支持：
1. 从Markdown中提取占位符
2. 清理AI模型返回的特殊标签
3. 提取Markdown代码块内容
"""

import re
import logging
from typing import Dict, List


logger = logging.getLogger(__name__)


class OCREngine:
    """OCR处理引擎"""

    def __init__(self, config: Dict = None):
        """
        初始化OCR引擎

        Args:
            config: 配置字典（可选）
        """
        self.config = config or {}

    # ========================================
    # 公共方法
    # ========================================

    def extract_placeholders(
        self,
        markdown: str,
        page_num: int = 0,
        start_index: int = 0,
        placeholder_pattern: str = None
    ) -> List[Dict]:
        """
        从Markdown中提取图片占位符

        Args:
            markdown: Markdown文本
            page_num: 页码（用于标记占位符来源）
            start_index: 起始索引（用于编号占位符）
            placeholder_pattern: 自定义占位符正则表达式（可选）
                默认匹配: <!-- IMAGE_PLACEHOLDER\ntype: ...\ndescription: ...\n-->

        Returns:
            占位符列表: [{
                'index': int,
                'page': int,
                'type': str,
                'description': str,
                'full_match': str
            }, ...]
        """
        if placeholder_pattern is None:
            # 默认匹配HTML注释格式（与v3脚本一致）
            placeholder_pattern = r'<!--\s*IMAGE_PLACEHOLDER\s+type:\s*(.+?)\s*description:\s*(.+?)\s*-->'

        placeholders = []
        matches = re.finditer(placeholder_pattern, markdown, re.DOTALL)

        for i, match in enumerate(matches):
            # HTML注释格式：group(1)=type, group(2)=description
            img_type = match.group(1).strip() if match.group(1) else '图片'
            detailed_desc = match.group(2).strip() if match.group(2) else ''

            placeholders.append({
                'index': start_index + i,
                'page': page_num,
                'type': img_type,
                'description': detailed_desc,
                'full_match': match.group(0)
            })

        logger.debug(f"从页面 {page_num + 1} 提取了 {len(placeholders)} 个占位符")

        return placeholders

    def clean_think_tags(self, content: str) -> str:
        """
        清理AI模型返回的think标签

        Args:
            content: 原始内容

        Returns:
            清理后的内容
        """
        # 移除think标签及其内容（支持多行）
        content = re.sub(r'<\|think\|>.*?<\|/think\|>', '', content, flags=re.DOTALL)

        # 清理多余空白
        content = content.strip()

        return content

    def extract_markdown_content(self, content: str) -> str:
        """
        从内容中提取Markdown代码块

        优先级：
        1. ```markdown ... ```
        2. ``` ... ```
        3. 返回原内容

        Args:
            content: 原始内容

        Returns:
            提取的Markdown内容
        """
        # 尝试提取 ```markdown 代码块
        markdown_pattern = r'```markdown\s*(.*?)\s*```'
        match = re.search(markdown_pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()

        # 尝试提取任意 ``` 代码块
        code_pattern = r'```\s*(.*?)\s*```'
        match = re.search(code_pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()

        # 如果没有代码块，返回原内容
        return content.strip()

    def count_placeholders(self, markdown: str) -> int:
        """
        统计Markdown中的占位符数量

        Args:
            markdown: Markdown文本

        Returns:
            占位符数量
        """
        pattern = r'!\[(.*?)\]\(IMAGE_PLACEHOLDER\)'
        matches = re.findall(pattern, markdown)
        return len(matches)

    def validate_placeholder_format(self, markdown: str) -> bool:
        """
        验证占位符格式是否正确

        Args:
            markdown: Markdown文本

        Returns:
            是否格式正确
        """
        pattern = r'!\[(.*?)\]\(IMAGE_PLACEHOLDER\)'
        matches = re.findall(pattern, markdown)

        for desc in matches:
            # 检查描述是否为空
            if not desc.strip():
                logger.warning(f"发现空描述的占位符")
                return False

        return True

    def get_placeholder_context(
        self,
        markdown: str,
        placeholder_match: str,
        context_lines: int = 3
    ) -> str:
        """
        获取占位符的上下文信息

        Args:
            markdown: 完整Markdown文本
            placeholder_match: 占位符完整匹配字符串
            context_lines: 上下文行数

        Returns:
            上下文文本
        """
        lines = markdown.split('\n')
        placeholder_line_idx = None

        # 找到占位符所在行
        for idx, line in enumerate(lines):
            if placeholder_match in line:
                placeholder_line_idx = idx
                break

        if placeholder_line_idx is None:
            return ""

        # 提取上下文
        start_idx = max(0, placeholder_line_idx - context_lines)
        end_idx = min(len(lines), placeholder_line_idx + context_lines + 1)

        context_lines_list = lines[start_idx:end_idx]

        return '\n'.join(context_lines_list)

    def replace_placeholder(
        self,
        markdown: str,
        placeholder_index: int,
        replacement: str,
        placeholders: List[Dict] = None
    ) -> str:
        """
        替换指定索引的占位符

        Args:
            markdown: Markdown文本
            placeholder_index: 占位符索引
            replacement: 替换内容
            placeholders: 占位符列表（可选，用于快速查找）

        Returns:
            替换后的Markdown文本
        """
        if placeholders:
            # 从占位符列表中查找
            target = None
            for p in placeholders:
                if p['index'] == placeholder_index:
                    target = p
                    break

            if target:
                markdown = markdown.replace(target['full_match'], replacement, 1)
                return markdown

        # 如果没有占位符列表，直接搜索替换
        # 这种方式不够精确，仅作为后备方案
        pattern = r'!\[(.*?)\]\(IMAGE_PLACEHOLDER\)'
        matches = list(re.finditer(pattern, markdown))

        if placeholder_index < len(matches):
            match = matches[placeholder_index]
            markdown = markdown[:match.start()] + replacement + markdown[match.end():]

        return markdown

    def clean_pdf_separators(self, markdown: str) -> str:
        """
        移除PDF页面分隔符（如 "--- Page N ---"）

        Args:
            markdown: Markdown文本

        Returns:
            清理后的Markdown文本
        """
        # 移除常见的页面分隔符模式
        patterns = [
            r'---\s*Page\s*\d+\s*---',  # --- Page 1 ---
            r'={3,}\s*第\s*\d+\s*页\s*={3,}',  # === 第 1 页 ===
            r'第\s*\d+\s*页',  # 第 1 页
            r'Page\s*\d+',  # Page 1
        ]

        for pattern in patterns:
            markdown = re.sub(pattern, '', markdown, flags=re.IGNORECASE)

        # 清理多余空行
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        return markdown.strip()
