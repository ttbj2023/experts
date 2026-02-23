#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片智能分析工具

支持后端：
1. Ollama (qwen3-vl:8b) - 本地模型，推荐
2. GLM-4.6V-Flash - 备用选项

分析图片内容，判断是否为数学公式、几何图形、示意图等
"""

import os
import base64
import json
import requests
import re
import logging
from typing import Dict, Optional
from pathlib import Path
import yaml

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """图片分析器 - 支持 Ollama 和 GLM-4.6V"""

    def __init__(self, config_path: str = "config/default.yaml", backend: str = "auto"):
        """
        初始化分析器

        Args:
            config_path: 配置文件路径
            backend: 后端选择 ("ollama", "glm", "auto")
        """
        # 加载配置
        self.config = self._load_config(config_path)
        self.backend = self._determine_backend(backend)

        # 初始化后端
        if self.backend == "ollama":
            # 修复导入路径
            try:
                from src.core.ollama_client import OllamaClient
            except ImportError:
                # 尝试相对导入
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from src.core.ollama_client import OllamaClient

            self.client = OllamaClient(self.config)
            logger.info("使用 Ollama 视觉模型")
        else:
            # GLM 后端
            self.api_url = self.config['models']['glm']['api_url'] + "/api/v1/chat"
            self.model = "glm-4.6v-flash"
            logger.info("使用 GLM-4.6V-Flash API")

        # 统计信息
        self.analysis_count = 0
        self.math_formula_count = 0
        self.geometry_count = 0
        self.other_count = 0

    def analyze_image(self, image_path: str) -> Dict:
        """
        分析图片类型

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

        # 委托给后端客户端
        if self.backend == "ollama":
            return self.client.analyze_image(image_path)
        else:
            return self._analyze_with_glm(image_path)

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
        从响应中提取JSON

        Args:
            content: API响应内容

        Returns:
            解析后的字典
        """
        # 清理内容
        content = content.strip()

        # 尝试直接解析
        try:
            return json.loads(content)
        except:
            pass

        # 尝试提取JSON代码块
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # 尝试提取花括号内容（可能包含嵌套）
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

    def get_stats(self) -> Dict:
        """获取统计信息"""
        if self.backend == "ollama":
            return self.client.get_stats()
        return {
            'total_analyzed': self.analysis_count,
            'math_formulas': self.math_formula_count,
            'geometry': self.geometry_count,
            'others': self.other_count
        }

    # ========================================
    # 私有方法
    # ========================================

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            # 尝试从项目根目录加载
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / config_path

            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"配置文件不存在: {config_file}，使用默认配置")
                return {
                    'models': {
                        'ollama': {
                            'api_url': 'http://localhost:11434',
                            'vision_model': 'qwen3-vl:8b',
                            'text_model': 'qwen3-vl:8b',
                            'timeout': 180
                        },
                        'glm': {
                            'api_url': 'http://192.168.100.110:9999',
                            'model': 'glm-4.6v-flash',
                            'enabled': True
                        }
                    }
                }
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}，使用默认配置")
            return {
                'models': {
                    'ollama': {
                        'api_url': 'http://localhost:11434',
                        'vision_model': 'qwen3-vl:8b',
                        'timeout': 180
                    }
                }
            }

    def _determine_backend(self, backend: str) -> str:
        """确定使用的后端"""
        if backend == "auto":
            # 优先使用 Ollama，如果 GLM 启用则使用 GLM
            if self.config['models'].get('glm', {}).get('enabled', False):
                return "glm"
            return "ollama"
        return backend

    def _analyze_with_glm(self, image_path: str) -> Dict:
        """使用 GLM-4.6V 分析图片"""
        # 读取图片并编码为base64
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"读取图片失败: {image_path}, {str(e)}")
            return self._default_result('读取失败', True)

        # 构建分析提示词
        prompt = """请分析这张图片，判断它的类型。请只返回JSON格式，不要添加任何其他文字：

1. math_formula (数学公式与符号): 包含数学符号、分数、方程、矩阵、求和符号、积分、几何标注符号等可用LaTeX表示的数学表达式和符号的图片
2. geometry (几何图形): 包含三角形、圆、函数图象、几何证明图等几何图形的图片
3. diagram (示意图/图表): 包含表格、统计图、流程图、示意图等的图片
4. other (其他): 其他类型的图片

请严格按照以下JSON格式返回：
{
  "type": "math_formula",
  "confidence": 0.95,
  "description": "简短描述"
}"""

        # 调用API
        try:
            request_data = {
                "model": self.model,
                "system_prompt": "你是一个专业的图片类型分析助手。请只返回JSON格式，不要添加任何解释。",
                "input": [
                    {
                        "type": "text",
                        "content": prompt
                    },
                    {
                        "type": "image",
                        "data_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            }

            logger.info(f"正在分析图片: {os.path.basename(image_path)}")

            response = requests.post(
                self.api_url,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # 解析响应 - output是数组，找到type="message"的内容
                if 'output' in result and isinstance(result['output'], list):
                    message_content = None
                    for item in result['output']:
                        if item.get('type') == 'message':
                            message_content = item.get('content', '')
                            break

                    if message_content:
                        analysis = self._parse_json_response(message_content)

                        # 统计
                        if analysis['type'] == 'math_formula':
                            self.math_formula_count += 1
                            analysis['should_keep'] = False
                        else:
                            self.geometry_count += 1 if analysis['type'] == 'geometry' else self.other_count
                            analysis['should_keep'] = True

                        logger.info(f"  → 类型: {analysis['type']}, 置信度: {analysis['confidence']}, 保留: {analysis['should_keep']}")

                        return analysis

                logger.warning(f"API响应格式异常")
                return self._default_result('响应格式错误', True)
            else:
                logger.warning(f"API调用失败: {response.status_code}")
                return self._default_result('API调用失败', True)

        except requests.exceptions.Timeout:
            logger.error(f"API调用超时: {image_path}")
            return self._default_result('超时', True)
        except Exception as e:
            logger.error(f"分析图片异常: {image_path}, {str(e)}")
            return self._default_result(f'异常: {str(e)}', True)

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


# 测试代码
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 image_analyzer.py <image_path>")
        print("示例: python3 image_analyzer.py /path/to/image.png")
        sys.exit(1)

    analyzer = ImageAnalyzer()

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"错误: 图片不存在: {image_path}")
        sys.exit(1)

    print(f"分析图片: {image_path}")
    result = analyzer.analyze_image(image_path)

    print("\n分析结果:")
    print(f"  类型: {result['type']}")
    print(f"  置信度: {result['confidence']}")
    print(f"  描述: {result['description']}")
    print(f"  是否保留: {result['should_keep']}")

    print("\n统计信息:")
    stats = analyzer.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

