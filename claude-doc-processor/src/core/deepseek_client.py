"""
DeepSeek 客户端

统一的DeepSeek API调用接口，支持：
1. 语义匹配 - 将图片占位符与实际图片进行智能匹配
2. 排版优化 - 优化OCR识别的Markdown格式
"""

import json
import re
import logging
from typing import Dict, List, Optional
import requests


logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API客户端"""

    def __init__(self, config: Dict):
        """
        初始化DeepSeek客户端

        Args:
            config: 配置字典，从config/default.yaml加载
        """
        self.api_key = config['models']['deepseek'].get('api_key', '')
        self.model = config['models']['deepseek']['model']
        self.timeout = config['models']['deepseek']['timeout']
        self.temperature = config['models']['deepseek']['temperature']
        self.max_tokens = config['models']['deepseek']['max_tokens']

        # 从环境变量读取API key（优先级更高）
        import os
        env_key = os.environ.get('DEEPSEEK_API_KEY')
        if env_key:
            self.api_key = env_key

    # ========================================
    # 公共方法
    # ========================================

    def semantic_matching(
        self,
        markdown: str,
        placeholders: List[Dict],
        images: List[Dict],
        prompt_template: Optional[str] = None
    ) -> Dict[int, str]:
        """
        将图片占位符与实际图片进行语义匹配（Stage 4）

        Args:
            markdown: 完整的Markdown文档内容
            placeholders: 占位符列表 [{index, page, type, description}, ...]
            images: 图片描述列表 [{filename, description}, ...]
            prompt_template: 自定义提示词模板（可选）

        Returns:
            匹配映射字典: {placeholder_index: image_filename}
        """
        if not self.api_key:
            logger.warning("未配置DeepSeek API密钥，跳过语义匹配")
            return {}

        logger.info("=" * 60)
        logger.info("DeepSeek 语义匹配")
        logger.info("=" * 60)
        logger.info(f"  占位符数量: {len(placeholders)}")
        logger.info(f"  图片数量: {len(images)}")

        # 构建prompt
        if prompt_template is None:
            prompt_template = """你是一个智能文档处理助手，负责将图片占位符与实际图片进行语义匹配，并返回JSON格式的匹配结果。

## 任务说明
我会给你：
1. **完整的Markdown文档内容**（包含所有占位符及其上下文）
2. 一组实际图片的描述（由视觉模型生成）

请你**仔细阅读整个文档，理解每个占位符在文档中的上下文**，然后将占位符匹配到最合适的图片。

## 匹配原则
1. **上下文理解**：优先根据占位符在文档中的位置和内容来判断
2. **语义相似度**：占位符描述的内容应该与图片描述的内容高度一致
3. **细节匹配**：关键元素（如形状、标注、文字、数量等）必须匹配
4. **一一对应**：每个占位符匹配一个唯一的图片，**每个图片只能匹配一个占位符**
5. **不存在重复匹配**：如果多个占位符看起来相似，只选择第一个最合适的匹配
6. **精确匹配**：如果找不到合适的匹配，就返回null，不要强行匹配

## 完整Markdown文档

```
{markdown_content}
```

## 占位符列表

{placeholders_list}

## 图片描述列表

{images_list}

## 输出要求

请严格按照以下JSON格式输出：

```json
{{
  "matches": [
    {{
      "placeholder_index": 0,
      "image_filename": "image5.png",
      "confidence": "高",
      "reason": "根据文档上下文，这是数轴图，图片描述完全匹配"
    }}
  ],
  "unmatched_placeholders": [1, 5],
  "unmatched_images": ["image10.png"]
}}
```

现在请开始匹配：
"""

        # 构建占位符列表
        placeholders_text = ""
        for p in placeholders:
            placeholders_text += f"\n**占位符 {p['index']}**\n"
            placeholders_text += f"- 页码: {p['page']}\n"
            placeholders_text += f"- 类型: {p.get('type', '未知')}\n"
            desc = p.get('description', '')[:200]
            placeholders_text += f"- 描述: {desc}...\n"

        # 构建图片列表
        images_text = ""
        for img in images:
            images_text += f"\n**{img['filename']}**\n"
            desc = img.get('description', '')[:300]
            images_text += f"- 描述: {desc}...\n"

        # 限制markdown长度（避免超过token限制）
        markdown_content = markdown[:30000]
        if len(markdown) > 30000:
            logger.warning(f"  Markdown过长({len(markdown)}字符)，截取前30000字符")

        # 填充prompt
        prompt = prompt_template.format(
            markdown_content=markdown_content,
            placeholders_list=placeholders_text,
            images_list=images_text
        )

        # 调试：打印prompt长度
        logger.info(f"  Prompt长度: {len(prompt)} 字符")
        logger.debug(f"  Prompt预览:\n{prompt[:500]}...")

        # 调用API
        try:
            result = self._call_api(
                prompt,
                response_format={"type": "json_object"},
                timeout=self.timeout
            )

            # 解析JSON结果
            content = result.get('content', '')
            match_result = json.loads(content)

            # 提取匹配映射
            matches = match_result.get('matches', [])
            mapping = {}

            for match in matches:
                placeholder_index = match.get('placeholder_index')
                image_filename = match.get('image_filename')
                if placeholder_index is not None and image_filename:
                    mapping[placeholder_index] = image_filename
                    logger.info(f"  ✓ 占位符 {placeholder_index} → {image_filename}")

            # 报告未匹配项
            unmatched = match_result.get('unmatched_placeholders', [])
            if unmatched:
                logger.warning(f"  未匹配的占位符: {unmatched}")

            logger.info(f"✅ 匹配完成! 匹配了 {len(mapping)} 个占位符")
            return mapping

        except json.JSONDecodeError as e:
            logger.error(f"  ❌ 解析JSON失败: {e}")
            logger.error(f"  返回内容: {content[:500] if 'content' in locals() else 'N/A'}")
            return {}
        except Exception as e:
            logger.error(f"  ❌ 语义匹配失败: {e}")
            return {}

    def format_markdown(
        self,
        markdown: str,
        prompt_template: Optional[str] = None
    ) -> str:
        """
        优化OCR识别的Markdown格式（Stage 1.5）

        Args:
            markdown: 待优化的Markdown文本
            prompt_template: 自定义提示词模板（可选）

        Returns:
            优化后的Markdown文本
        """
        if not self.api_key:
            logger.warning("未配置DeepSeek API密钥，跳过排版优化")
            return markdown

        logger.info("=" * 60)
        logger.info("DeepSeek 排版优化")
        logger.info("=" * 60)
        logger.info(f"  输入字符数: {len(markdown):,}")

        if prompt_template is None:
            prompt_template = """你是一个专业的Markdown排版专家。请对以下OCR识别的Markdown文本进行排版优化。

## 排版要求

### 1. 标题层级规范
- 一级标题：使用 `#` （如：# 一、茶树的起源）
- 二级标题：使用 `##` （如：## (一) 茶树起源的佐证）
- 三级标题：使用 `###` （如：### 1. 最早的茶字）
- 四级标题：使用 `####` （如：#### (1) "茶"字的由来）
- 五级标题：使用 `#####` （如：##### ① 若）

规则：
- 标题序号保留中文数字（一、二、三）和阿拉伯数字（1、2、3）
- 括号标题保留括号（（一）、(1)）
- 列表标记（①②③）前添加 `##### ` 作为五级标题

### 2. 列表格式规范
- 无序列表：使用 `- ` 开头（如：- 第一点）
- 有序列表：使用 `1. ` 开头（如：1. 第一步）
- 嵌套列表：使用缩进（2空格或4空格）

### 3. 页面连接处理
- 移除页面之间的断句（如孤立的句子片段）
- 保持段落的完整性
- 移除误识别的页码（如单独成行的数字）

### 4. 文本清理
- 移除多余空行（保留1个空行分隔段落）
- 移除行首行尾多余空格
- 修复明显的OCR错误

### 5. 格式统一
- 标题与内容之间保留1个空行
- 段落之间保留1个空行
- 列表项之间不保留空行

## 输入文本

```
{markdown_content}
```

## 输出要求

1. **只输出优化后的Markdown内容**，不要有解释或前言
2. 保持原意不变，只优化格式
3. 不要删除任何内容
4. 输出必须是纯Markdown格式，不要使用markdown代码块包裹

现在请开始排版优化：
"""

        # 填充prompt
        prompt = prompt_template.format(markdown_content=markdown)

        try:
            # 分段处理超长文档
            if len(markdown) > 50000:
                logger.warning(f"  文档过长({len(markdown)}字符)，将分段处理")
                formatted_text = self._format_long_document(markdown, prompt_template)
            else:
                result = self._call_api(prompt, timeout=300)
                formatted_text = result.get('content', '').strip()

                # 移除可能的markdown代码块包裹
                formatted_text = self._remove_code_block_markers(formatted_text)

            logger.info(f"  输出字符数: {len(formatted_text):,}")
            logger.info("✅ 排版优化完成")

            return formatted_text

        except Exception as e:
            logger.error(f"❌ 排版优化失败: {e}")
            logger.warning("将使用原始Markdown继续处理")
            return markdown

    # ========================================
    # 私有方法
    # ========================================

    def _call_api(
        self,
        prompt: str,
        response_format: Optional[Dict] = None,
        timeout: int = 120
    ) -> Dict:
        """
        调用DeepSeek API

        Args:
            prompt: 提示词
            response_format: 响应格式（如 {"type": "json_object"}）
            timeout: 超时时间（秒）

        Returns:
            API响应内容

        Raises:
            requests.HTTPError: API调用失败
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }

        # 添加响应格式（如果指定）
        if response_format:
            payload["response_format"] = response_format

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )

        # 调试：打印错误详情
        if response.status_code != 200:
            logger.error(f"  API返回错误 {response.status_code}")
            logger.error(f"  请求payload: {json.dumps(payload, ensure_ascii=False)[:500]}...")
            logger.error(f"  响应内容: {response.text[:500]}")

        response.raise_for_status()
        result = response.json()

        # 提取content
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        return {'content': content, 'raw': result}

    def _split_document(self, markdown: str, max_chars: int = 64000) -> List[str]:
        """
        将长文档分段

        Args:
            markdown: Markdown文档
            max_chars: 每段最大字符数

        Returns:
            分段后的文档列表
        """
        chunks = []
        current_chunk = ""
        lines = markdown.split('\n')

        for line in lines:
            if len(current_chunk) + len(line) + 1 > max_chars:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = line
            else:
                if current_chunk:
                    current_chunk += '\n' + line
                else:
                    current_chunk = line

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _format_long_document(
        self,
        markdown: str,
        prompt_template: str
    ) -> str:
        """
        处理超长文档的排版优化

        Args:
            markdown: Markdown文档
            prompt_template: 提示词模板

        Returns:
            优化后的完整文档
        """
        chunks = self._split_document(markdown, max_chars=50000)
        formatted_chunks = []

        logger.info(f"  分成 {len(chunks)} 段处理")

        for i, chunk in enumerate(chunks, 1):
            logger.info(f"  处理第 {i}/{len(chunks)} 段...")
            prompt = prompt_template.format(markdown_content=chunk)
            result = self._call_api(prompt, timeout=300)
            formatted = result.get('content', '').strip()
            formatted = self._remove_code_block_markers(formatted)
            formatted_chunks.append(formatted)

        return '\n\n'.join(formatted_chunks)

    def _remove_code_block_markers(self, text: str) -> str:
        """
        移除markdown代码块标记

        Args:
            text: 原始文本

        Returns:
            移除标记后的文本
        """
        # 移除开头的 ```markdown 或 ```
        if text.startswith('```markdown'):
            text = text[13:].lstrip()
        elif text.startswith('```'):
            text = text[3:].lstrip()

        # 移除结尾的 ```
        if text.endswith('```'):
            text = text[:-3].rstrip()

        return text.strip()
