"""
DOCX转换器

将DOCX文档转换为Markdown，支持：
- LibreOffice转换 + GLM OCR
- 图片提取和描述
- DeepSeek语义匹配（全局上下文）
- 智能占位符替换
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from .base import BaseConverter
from ..core.glm_client import GLMClient
from ..core.deepseek_client import DeepSeekClient
from ..core.image_processor import ImageProcessor
from ..core.ocr_engine import OCREngine


class DOCXConverter(BaseConverter):
    """
    DOCX转Markdown转换器（v3三阶段架构）

    使用4阶段架构：
    - Stage 1: DOCX图片提取 + LibreOffice转换 + GLM识别
    - Stage 2: GLM图片描述
    - Stage 3: DeepSeek语义匹配（全局上下文）
    - Stage 4: 智能占位符替换
    """

    def __init__(self, config_path: str = None):
        """初始化DOCX转换器"""
        super().__init__(config_path)

        # 初始化核心组件
        self.glm_client = GLMClient(self.config)
        self.deepseek_client = DeepSeekClient(self.config)
        self.image_processor = ImageProcessor(self.config)
        self.ocr_engine = OCREngine(self.config)

        # DOCX处理配置
        self.docx_config = self.config.get('processing', {}).get('docx', {})
        self.enable_code_cleanup = self.docx_config.get('enable_code_block_cleanup', True)
        self.enable_separator_cleanup = self.docx_config.get('enable_separator_cleanup', True)
        self.enable_duplicate_detection = self.docx_config.get('enable_duplicate_detection', True)
        self.enable_deepseek_formatting = self.docx_config.get('enable_deepseek_formatting', False)  # 新增：DeepSeek格式校对开关

    def convert(
        self,
        input_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[bool, str, Dict]:
        """
        执行DOCX到Markdown的完整转换流程

        Args:
            input_path: DOCX文件路径
            output_dir: 输出目录
            **kwargs: 额外参数

        Returns:
            (成功状态, 输出文件路径, 统计信息)
        """
        self._start_timer()

        # 验证输入
        if not self._validate_input_file(input_path, ['.docx', '.doc']):
            return False, '', self.stats

        # 创建输出目录
        if not self._create_output_dir(output_dir):
            return False, '', self.stats

        self.logger.info("\n" + "=" * 70)
        self.logger.info("DOCX → Markdown 转换流程（v3三阶段架构）")
        self.logger.info("=" * 70)
        self.logger.info(f"输入: {input_path}")
        self.logger.info(f"输出: {output_dir}")

        # 准备路径
        basename = Path(input_path).stem
        pdf_path = os.path.join(output_dir, f'{basename}.pdf')
        md_path = os.path.join(output_dir, f'{basename}_raw.md')
        images_dir = os.path.join(output_dir, 'extracted_images')

        try:
            # ========== Stage 1: DOCX图片提取 + LibreOffice转换 + GLM识别 ==========
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Stage 1: DOCX图片提取 + LibreOffice转换 + GLM识别")
            self.logger.info("=" * 60)

            # 1.1 从DOCX提取图片
            self.logger.info("  步骤1.1: 从DOCX提取图片...")
            docx_images, _ = self.image_processor.extract_from_docx(input_path, images_dir)
            self.logger.info(f"  ✓ 提取了 {len(docx_images)} 张图片")
            self.stats['total_images'] = len(docx_images)

            # 1.2 DOCX → PDF (LibreOffice)
            self.logger.info("  步骤1.2: DOCX → PDF (LibreOffice)...")
            pdf_success = self._convert_docx_to_pdf(input_path, pdf_path)
            if not pdf_success:
                raise Exception("DOCX转PDF失败")
            self.logger.info(f"  ✓ PDF生成成功")

            # 1.3 PDF → Markdown (GLM-4.6V-Flash with placeholders)
            self.logger.info("  步骤1.3: PDF → Markdown (GLM-4.6V-Flash)...")
            markdown_content = self._convert_pdf_with_glm46v(pdf_path, md_path)
            self.logger.info(f"  ✓ Markdown生成成功（带占位符）")

            self.stats['stages_completed'].append('Stage 1: OCR + 占位符')

            # ========== Stage 2: GLM图片描述 ==========
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Stage 2: GLM-4.6V-Flash 图片描述")
            self.logger.info("=" * 60)

            image_descriptions = self._describe_images(docx_images, images_dir)
            self.stats['stages_completed'].append('Stage 2: GLM图片描述')

            # ========== Stage 3: DeepSeek语义匹配（全局上下文） ==========
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Stage 3: DeepSeek 语义匹配（全局上下文）")
            self.logger.info("=" * 60)

            # 提取占位符
            placeholders = self.ocr_engine.extract_placeholders(markdown_content)

            # 语义匹配
            mapping = self.deepseek_client.semantic_matching(
                markdown_content,
                placeholders,
                image_descriptions
            )

            self.stats['matched_images'] = len(mapping)
            self.stats['stages_completed'].append('Stage 3: DeepSeek语义匹配')

            # ========== Stage 4: 智能占位符替换 ==========
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Stage 4: 智能占位符替换")
            self.logger.info("=" * 60)

            final_markdown = self._replace_placeholders_intelligently(
                markdown_content,
                placeholders,
                mapping,
                images_dir
            )
            self.stats['stages_completed'].append('Stage 4: 智能占位符替换')

            # ========== Stage 5: DeepSeek格式校对（可选） ==========
            if self.enable_deepseek_formatting:
                self.logger.info("\n" + "=" * 60)
                self.logger.info("Stage 5: DeepSeek 格式校对（高精度模式）")
                self.logger.info("=" * 60)

                final_markdown = self._format_with_deepseek(final_markdown)
                self.stats['stages_completed'].append('Stage 5: DeepSeek格式校对')

            # 保存最终结果
            output_file = self._get_output_filename(input_path, output_dir)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            self.stats['input_file'] = input_path
            self.stats['output_file'] = output_file

            # 清理临时文件
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            # 保存元数据和统计
            self._save_metadata(output_dir, self.stats)
            self._stop_timer()

            # 输出统计信息
            self._log_stats(self.stats)

            return True, output_file, self.stats

        except Exception as e:
            self.logger.error(f"❌ 转换失败: {e}")
            self._stop_timer()
            self.stats['error'] = str(e)
            return False, '', self.stats

    # ========================================
    # 辅助方法
    # ========================================

    def _convert_docx_to_pdf(self, docx_path: str, pdf_path: str) -> bool:
        """使用LibreOffice将DOCX转换为PDF"""
        try:
            output_dir = os.path.dirname(pdf_path)
            docx_name = Path(docx_path).stem
            expected_pdf_name = f"{docx_name}.pdf"
            expected_pdf_path = os.path.join(output_dir, expected_pdf_name)

            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                docx_path
            ]

            self.logger.info(f"执行命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.docx_config.get('libreoffice_timeout', 60)
            )

            if result.returncode != 0:
                self.logger.error(f"LibreOffice转换失败: {result.stderr.decode('utf-8', errors='ignore')}")
                return False

            # LibreOffice会使用原文件名，可能需要重命名
            if expected_pdf_path != pdf_path and os.path.exists(expected_pdf_path):
                os.rename(expected_pdf_path, pdf_path)

            return os.path.exists(pdf_path)

        except subprocess.TimeoutExpired:
            self.logger.error("LibreOffice转换超时")
            return False
        except Exception as e:
            self.logger.error(f"LibreOffice转换失败: {e}")
            return False

    def _convert_pdf_with_glm46v(self, pdf_path: str, md_path: str) -> str:
        """使用GLM-4.6V-Flash将PDF转换为Markdown（带占位符）"""
        import fitz

        pdf = fitz.open(pdf_path)
        all_markdown = []

        for page_num in range(len(pdf)):
            self.logger.info(f"  处理第 {page_num + 1}/{len(pdf)} 页...")

            # 渲染页面
            page = pdf[page_num]
            dpi = self.docx_config.get('image_max_size', 1280) // 4  # 估算DPI
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)

            temp_image = f'/tmp/docx_page_{page_num + 1}.png'
            pix.save(temp_image)

            # GLM OCR识别
            markdown = self.glm_client.ocr_page(temp_image)
            all_markdown.append(markdown)

            # 删除临时图片
            os.remove(temp_image)

        pdf.close()

        # 合并所有页面
        final_markdown = '\n\n'.join(all_markdown)

        return final_markdown

    def _describe_images(self, docx_images: List[Dict], images_dir: str) -> List[Dict]:
        """描述所有图片"""
        self.logger.info(f"  开始描述 {len(docx_images)} 张图片...")

        image_descriptions = []

        for idx, img_info in enumerate(docx_images, 1):
            filename = img_info['filename']
            image_path = os.path.join(images_dir, filename)

            self.logger.info(f"  [{idx}/{len(docx_images)}] 描述 {filename}...")

            try:
                description = self.glm_client.describe_image(image_path)
                image_descriptions.append({
                    'filename': filename,
                    'description': description
                })
                self.logger.info(f"  ✓ {description[:80]}...")
            except Exception as e:
                self.logger.error(f"  ❌ 描述失败: {e}")
                image_descriptions.append({
                    'filename': filename,
                    'description': f"描述失败: {str(e)}"
                })

        return image_descriptions

    def _replace_placeholders_intelligently(
        self,
        markdown: str,
        placeholders: List[Dict],
        mapping: Dict[int, str],
        images_dir: str
    ) -> str:
        """智能替换占位符"""
        # 移除无效代码块
        if self.enable_code_cleanup:
            markdown = self._remove_invalid_code_blocks(markdown)

        # 移除PDF分隔符
        if self.enable_separator_cleanup:
            markdown = self.ocr_engine.clean_pdf_separators(markdown)

        # 检测并处理重复匹配
        if self.enable_duplicate_detection:
            mapping = self._detect_and_remove_duplicates(mapping)

        # 替换占位符
        for placeholder in sorted(placeholders, key=lambda x: x['index'], reverse=True):
            idx = placeholder['index']
            full_match = placeholder['full_match']

            if idx in mapping:
                image_filename = mapping[idx]
                image_path = os.path.join('extracted_images', image_filename)

                markdown = markdown.replace(
                    full_match,
                    f'![{placeholder.get("type", "图片")}]({image_path})',
                    1
                )
            else:
                # 移除未匹配的占位符
                markdown = markdown.replace(full_match, '', 1)

        self.logger.info(f"  ✓ 替换了 {len(mapping)} 个占位符")

        return markdown

    def _remove_invalid_code_blocks(self, content: str) -> str:
        """移除GLM误识别的无效代码块"""
        import re

        # 定义有效的编程语言标签（只保留这些语言的代码块）
        valid_languages = {
            'markdown', 'python', 'py', 'javascript', 'js', 'java',
            'c', 'cpp', 'c++', 'go', 'rust', 'ruby', 'php', 'swift',
            'kotlin', 'typescript', 'ts', 'shell', 'bash', 'sql',
            'html', 'css', 'xml', 'json', 'yaml', 'yml'
        }

        # 保留有效语言的代码块，移除其他代码块的标记
        def replace_code_block(match):
            lang = match.group(1).lower() if match.group(1) else ''
            if lang in valid_languages:
                # 保留代码块标记
                return match.group(0)
            else:
                # 移除代码块标记，只保留内容
                return match.group(2)

        # 匹配代码块：```语言标识符（可选）+ 内容 + ```
        pattern = r'```(\w*)\n(.*?)\n```'
        valid_content = re.sub(pattern, replace_code_block, content, flags=re.DOTALL)

        return valid_content

    def _detect_and_remove_duplicates(self, mapping: Dict[int, str]) -> Dict[int, str]:
        """检测并移除重复匹配"""
        # 统计每个图片被匹配的次数
        image_counts = {}
        for placeholder_idx, image_filename in mapping.items():
            if image_filename not in image_counts:
                image_counts[image_filename] = []
            image_counts[image_filename].append(placeholder_idx)

        # 移除重复匹配，只保留第一个
        cleaned_mapping = {}
        for placeholder_idx, image_filename in mapping.items():
            if image_counts[image_filename][0] == placeholder_idx:
                cleaned_mapping[placeholder_idx] = image_filename
            else:
                self.logger.warning(f"  ⚠️  检测到重复匹配，移除占位符 {placeholder_idx} → {image_filename}")

        return cleaned_mapping

    def _format_with_deepseek(self, markdown_content: str) -> str:
        """使用DeepSeek进行格式校对
        
        Args:
            markdown_content: 待校对的Markdown内容
            
        Returns:
            校对后的Markdown内容
        """
        self.logger.info("  正在调用DeepSeek进行格式校对...")
        
        prompt = """你是一个专业的Markdown格式校对专家。请校对以下Markdown文档的格式。

## 校对要求

### 1. 数学符号处理（最重要！）

**遵循"简单用Unicode，复杂用LaTeX"原则**

**优先使用Unicode字符：**
- 希腊字母：`α = 30°`、`π ≈ 3.14`、`θ > 0`
- 运算符号：`a × b`、`a ÷ b`、`a ± b`
- 比较符号：`a ≠ b`、`a ≤ b`、`a ≥ b`、`a ≈ b`
- 特殊符号：`∞`、`°`、`√2`、`²`、`³`

**必须用LaTeX $...$ 包裹：**
- 分数：`$\frac{1}{2}$`、`$\frac{a+b}{c-d}$`
- 复杂上下标：`$x_1$`、`$x^{n+1}$`、`$10^{-6}$`
- 几何符号：`$\widehat{AB}$`、`$\angle ABC$`、`$\triangle ABC$`
- 求和积分：`$\sum_{i=1}^{n}$`、`$\int_0^1$`

### 2. 标题层级规范
- 一级标题：`#`
- 二级标题：`##`
- 三级标题：`###`
- 确保层级正确，不要越级

### 3. 清理多余空行
- 段落之间保留1个空行
- 标题前后保留1个空行
- 列表项之间不留空行
- 删除连续的多个空行

### 4. 列表格式
- 无序列表使用 `- ` 开头
- 有序列表使用 `1. ` 开头
- 确保缩进一致（2空格或4空格）

### 5. 表格格式
- 使用标准Markdown表格语法
- 确保列对齐（使用 `:---` 控制对齐方式）

### 6. 代码块
- 只保留有效的编程语言代码块
- 移除误识别的普通文本代码块

## 输出要求

1. **只输出校对后的Markdown内容**，不要有解释或前言
2. 保持原意不变，只优化格式
3. 不要删除任何内容
4. 输出必须是纯Markdown格式，不要使用markdown代码块包裹

---

请校对以下Markdown内容：

"""
        
        try:
            # 调用DeepSeek API
            formatted = self.deepseek_client.chat(prompt + markdown_content)
            
            # 清理可能的markdown代码块包裹
            if formatted.startswith('```markdown'):
                formatted = formatted.replace('```markdown', '', 1)
            if formatted.startswith('```'):
                formatted = formatted.replace('```', '', 1)
            if formatted.endswith('```'):
                formatted = formatted[:-3]
            
            formatted = formatted.strip()
            
            self.logger.info("  ✓ 格式校对完成")
            return formatted
            
        except Exception as e:
            self.logger.warning(f"  ⚠️  格式校对失败: {e}，返回原始内容")
            return markdown_content
