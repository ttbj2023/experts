#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama 客户端

统一的 Ollama API 调用接口，支持：
1. 视觉模型 - qwen3-vl:8b 进行图片分析和描述
2. 文本模型 - 用于语义匹配和排版优化
"""

import base64
import json
import logging
import requests
from typing import Dict, List, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama API 客户端"""

    def __init__(self, config: Dict):
        """
        初始化 Ollama 客户端

        Args:
            config: 配置字典，从 config/default.yaml 加载
        """
        self.api_url = config['models'].get('ollama', {}).get('api_url', 'http://localhost:11434')
        self.vision_model = config['models'].get('ollama', {}).get('vision_model', 'qwen3-vl:8b')
        self.text_model = config['models'].get('ollama', {}).get('text_model', 'qwen3-vl:8b')
        self.timeout = config['models'].get('ollama', {}).get('timeout', 120)

        # 统计信息
        self.analysis_count = 0
        self.math_formula_count = 0
        self.geometry_count = 0
        self.other_count = 0

        logger.info(f"Ollama 客户端初始化: {self.api_url}")
        logger.info(f"  视觉模型: {self.vision_model}")
        logger.info(f"  文本模型: {self.text_model}")

    # ========================================
    # 视觉模型方法
    # ========================================

    def analyze_image(self, image_path: str) -> Dict:
        """
        分析图片类型（使用 qwen3-vl:8b）

        Args:
            image_path: 图片路径

        Returns:
            分析结果字典:
            {
                'type': 'math_formula' | 'geometry' | 'diagram' | 'other',
                'confidence': 0.0-1.0,
                'description': '图片描述',
                'should_keep': bool
            }
        """
        self.analysis_count += 1

        # 读取图片
        image_base64 = self._read_image_base64(image_path)
        if not image_base64:
            logger.error(f"读取图片失败: {image_path}")
            return self._default_result('读取失败', True)

        # 构建分析提示词
        prompt = """请分析这张图片，判断它的类型。请只返回JSON格式，不要添加任何其他文字：

1. math_formula (数学公式与符号): 包含数学符号、分数、方程、矩阵、求和符号、积分、几何标注符号等可用LaTeX表示的数学表达式和符号的图片
   - 例如：分数(1/2)、方程(x²+2x=0)、根号(√)、求和(∑)、积分(∫)
   - 例如：几何标注符号(弧AD、角度∠ABC、垂直⊥、平行∥、度数°、上标²、下标ₙ)
   - 判断标准：图片内容主要是数学符号、公式或标注，可以用LaTeX简洁表示，且不需要保留图形结构

2. geometry (几何图形): 包含三角形、圆、函数图象、几何证明图等几何图形的图片
   - 例如：三角形、圆、四边形、函数曲线图、坐标系图、立体图形
   - 判断标准：图片包含完整的几何图形或图象，需要保留图形的视觉结构

3. diagram (示意图/图表): 包含表格、统计图、流程图、示意图等的图片
   - 例如：数据表格、柱状图、饼图、流程图、组织结构图
   - 判断标准：图片是用于展示信息、数据或过程的图表

4. other (其他): 其他类型的图片

请严格按照以下JSON格式返回：
{
  "type": "math_formula",
  "confidence": 0.95,
  "description": "简短描述"
}

判断优先级：
- 如果是纯数学符号/公式/标注 → math_formula（即使包含字母如AD、ABC）
- 如果是几何图形结构 → geometry
- 如果是数据图表 → diagram"""

        try:
            logger.info(f"正在分析图片: {Path(image_path).name}")

            # 调用 Ollama API
            response = self._call_vision_api(prompt, image_base64)

            if response:
                # 解析响应
                analysis = self._parse_json_response(response)

                # 统计
                if analysis['type'] == 'math_formula':
                    self.math_formula_count += 1
                    analysis['should_keep'] = False
                elif analysis['type'] == 'geometry':
                    self.geometry_count += 1
                    analysis['should_keep'] = True
                else:
                    self.other_count += 1
                    analysis['should_keep'] = True

                logger.info(f"  → 类型: {analysis['type']}, 置信度: {analysis['confidence']}, 保留: {analysis['should_keep']}")

                return analysis
            else:
                logger.warning(f"API响应为空")
                return self._default_result('无有效响应', True)

        except Exception as e:
            logger.error(f"分析图片异常: {image_path}, {str(e)}")
            return self._default_result(f'异常: {str(e)}', True)

    def describe_image(self, image_path: str, detail_level: str = 'standard') -> str:
        """
        生成图片描述（使用 qwen3-vl:8b）

        Args:
            image_path: 图片路径
            detail_level: 描述详细程度 ('brief', 'standard', 'detailed')

        Returns:
            图片描述文本
        """
        # 读取图片
        image_base64 = self._read_image_base64(image_path)
        if not image_base64:
            return "无法读取图片"

        # 根据详细程度构建提示词
        if detail_level == 'brief':
            prompt = "请用一句话简洁描述这张图片的内容。只返回描述，不要有其他内容。"
        elif detail_level == 'detailed':
            prompt = """请详细描述这张图片的内容，包括：
1. 图片的类型（几何图形、数学公式、统计图表、示意图等）
2. 图片中的关键元素和细节
3. 如果有文字或标注，请准确引用
4. 各元素之间的关系和位置

请直接返回描述文本，不要添加任何前言或解释。"""
        else:  # standard
            prompt = """请详细描述这张图片的内容。

要求：
1. 识别图片的类型（几何图形、数学公式、统计图表、示意图等）
2. 描述图片中的关键元素和细节
3. 如果有文字或标注，请准确引用
4. 描述要准确、简洁，不超过200字

请直接返回描述文本，不要添加其他内容。"""

        try:
            logger.info(f"正在生成描述: {Path(image_path).name}")

            # 调用 Ollama API
            response = self._call_vision_api(prompt, image_base64)

            if response:
                # 清理响应
                description = response.strip()
                # 移除可能的引号包裹
                if description.startswith('"') and description.endswith('"'):
                    description = description[1:-1]

                logger.info(f"  → 描述: {description[:100]}...")
                return description
            else:
                logger.warning(f"API响应为空")
                return "无法生成图片描述"

        except Exception as e:
            logger.error(f"生成描述异常: {image_path}, {str(e)}")
            return f"生成描述失败: {str(e)}"

    # ========================================
    # 文本模型方法
    # ========================================

    def semantic_matching(
        self,
        markdown: str,
        placeholders: List[Dict],
        images: List[Dict],
        prompt_template: Optional[str] = None
    ) -> Dict[int, str]:
        """
        将图片占位符与实际图片进行语义匹配

        Args:
            markdown: 完整的 Markdown 文档内容
            placeholders: 占位符列表
            images: 图片描述列表
            prompt_template: 自定义提示词模板（可选）

        Returns:
            匹配映射字典: {placeholder_index: image_filename}
        """
        logger.info("=" * 60)
        logger.info("Ollama 语义匹配")
        logger.info("=" * 60)
        logger.info(f"  占位符数量: {len(placeholders)}")
        logger.info(f"  图片数量: {len(images)}")

        # 构建默认提示词
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

现在请开始匹配："""

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

        # 限制 markdown 长度
        markdown_content = markdown[:30000]
        if len(markdown) > 30000:
            logger.warning(f"  Markdown过长({len(markdown)}字符)，截取前30000字符")

        # 填充提示词
        prompt = prompt_template.format(
            markdown_content=markdown_content,
            placeholders_list=placeholders_text,
            images_list=images_text
        )

        logger.info(f"  Prompt长度: {len(prompt)} 字符")

        try:
            # 调用文本模型 API
            response = self._call_text_api(prompt, format='json')

            if response:
                # 解析 JSON 结果
                match_result = json.loads(response)

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
            else:
                logger.error("❌ API响应为空")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"❌ 解析JSON失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ 语义匹配失败: {e}")
            return {}

    def format_markdown(
        self,
        markdown: str,
        prompt_template: Optional[str] = None
    ) -> str:
        """
        优化OCR识别的Markdown格式

        Args:
            markdown: 待优化的Markdown文本
            prompt_template: 自定义提示词模板（可选）

        Returns:
            优化后的Markdown文本
        """
        logger.info("=" * 60)
        logger.info("Ollama 排版优化")
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

现在请开始排版优化："""

        # 填充提示词
        prompt = prompt_template.format(markdown_content=markdown)

        try:
            # 调用文本模型 API
            response = self._call_text_api(prompt)

            if response:
                # 移除可能的 markdown 代码块包裹
                formatted_text = self._remove_code_block_markers(response.strip())
                logger.info(f"  输出字符数: {len(formatted_text):,}")
                logger.info("✅ 排版优化完成")
                return formatted_text
            else:
                logger.error("❌ API响应为空")
                return markdown

        except Exception as e:
            logger.error(f"❌ 排版优化失败: {e}")
            logger.warning("将使用原始Markdown继续处理")
            return markdown

    # ========================================
    # 私有方法
    # ========================================

    def _read_image_base64(self, image_path: str) -> Optional[str]:
        """读取图片并返回 base64 编码"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"读取图片失败: {image_path}, {str(e)}")
            return None

    def _call_vision_api(self, prompt: str, image_base64: str) -> Optional[str]:
        """
        调用 Ollama 视觉模型 API

        Args:
            prompt: 提示词
            image_base64: 图片的 base64 编码

        Returns:
            模型响应文本
        """
        url = f"{self.api_url}/api/chat"

        payload = {
            "model": self.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # 提取响应内容
            if 'message' in result and 'content' in result['message']:
                return result['message']['content']
            else:
                logger.warning(f"意外的API响应格式: {result.keys()}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"API调用超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败: {str(e)}")
            return None

    def _call_text_api(self, prompt: str, format: str = 'text') -> Optional[str]:
        """
        调用 Ollama 文本模型 API

        Args:
            prompt: 提示词
            format: 输出格式 ('text' 或 'json')

        Returns:
            模型响应文本
        """
        url = f"{self.api_url}/api/generate"

        payload = {
            "model": self.text_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }

        # 添加格式选项（Ollama 支持 format 参数）
        if format == 'json':
            payload['format'] = 'json'

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # 提取响应内容
            if 'response' in result:
                return result['response']
            else:
                logger.warning(f"意外的API响应格式: {result.keys()}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"API调用超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败: {str(e)}")
            return None

    def _default_result(self, description: str, should_keep: bool) -> Dict:
        """返回默认结果"""
        return {
            'type': 'other',
            'confidence': 0.0,
            'description': description,
            'should_keep': should_keep
        }

    def _parse_json_response(self, content: str) -> Dict:
        """
        从响应中提取 JSON

        Args:
            content: API 响应内容

        Returns:
            解析后的字典
        """
        import re

        # 清理内容
        content = content.strip()

        # 尝试直接解析
        try:
            return json.loads(content)
        except:
            pass

        # 尝试提取 JSON 代码块
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # 尝试提取花括号内容
        brace_match = re.search(r'\{[^{}]*"type"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except:
                pass

        # 降级：从文本中推断类型
        content_lower = content.lower()

        if 'math_formula' in content_lower or '数学公式' in content_lower:
            img_type = 'math_formula'
            confidence = 0.7
        elif 'geometry' in content_lower or '几何' in content_lower:
            img_type = 'geometry'
            confidence = 0.7
        elif 'diagram' in content_lower or '示意图' in content_lower or '图表' in content_lower or '表格' in content_lower:
            img_type = 'diagram'
            confidence = 0.7
        else:
            img_type = 'other'
            confidence = 0.5

        return {
            'type': img_type,
            'confidence': confidence,
            'description': content[:100] if len(content) > 100 else content
        }

    def _remove_code_block_markers(self, text: str) -> str:
        """移除 markdown 代码块标记"""
        # 移除开头的 ```markdown 或 ```
        if text.startswith('```markdown'):
            text = text[13:].lstrip()
        elif text.startswith('```'):
            text = text[3:].lstrip()

        # 移除结尾的 ```
        if text.endswith('```'):
            text = text[:-3].rstrip()

        return text.strip()

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_analyzed': self.analysis_count,
            'math_formulas': self.math_formula_count,
            'geometry': self.geometry_count,
            'others': self.other_count
        }


# 测试代码
if __name__ == "__main__":
    import sys

    # 测试配置
    test_config = {
        'models': {
            'ollama': {
                'api_url': 'http://localhost:11434',
                'vision_model': 'qwen3-vl:8b',
                'text_model': 'qwen3-vl:8b',
                'timeout': 120
            }
        }
    }

    client = OllamaClient(test_config)

    if len(sys.argv) < 2:
        print("用法: python3 ollama_client.py <image_path>")
        print("示例: python3 ollama_client.py /path/to/image.png")
        sys.exit(1)

    image_path = sys.argv[1]
    if not Path(image_path).exists():
        print(f"错误: 图片不存在: {image_path}")
        sys.exit(1)

    print(f"分析图片: {image_path}")
    result = client.analyze_image(image_path)

    print("\n分析结果:")
    print(f"  类型: {result['type']}")
    print(f"  置信度: {result['confidence']}")
    print(f"  描述: {result['description']}")
    print(f"  是否保留: {result['should_keep']}")

    print("\n生成描述:")
    description = client.describe_image(image_path)
    print(f"  {description}")

    print("\n统计信息:")
    stats = client.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
