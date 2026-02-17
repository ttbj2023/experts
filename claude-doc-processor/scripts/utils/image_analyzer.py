#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片智能分析工具

使用本地GLM-4.6V-Flash API分析图片内容
判断是否为数学公式、几何图形、示意图等
"""

import os
import base64
import json
import requests
import re
import logging
from typing import Dict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """图片分析器 - 使用本地GLM-4.6V-Flash API"""

    def __init__(self, api_url: str = "http://192.168.100.110:9999/api/v1/chat"):
        """
        初始化分析器

        Args:
            api_url: 本地GLM-4.6V-Flash API地址
        """
        self.api_url = api_url
        self.model = "glm-4.6v-flash"

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

        # 调用API
        try:
            # 构建请求数据 - GLM-4.6V支持多模态
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
                    # 查找message类型的内容
                    message_content = None
                    for item in result['output']:
                        if item.get('type') == 'message':
                            message_content = item.get('content', '')
                            break

                    if message_content:
                        # 解析JSON
                        analysis = self._parse_json_response(message_content)

                        # 统计
                        if analysis['type'] == 'math_formula':
                            self.math_formula_count += 1
                            analysis['should_keep'] = False  # 数学公式不需要保留（GLM已转为LaTeX）
                        else:
                            self.geometry_count += 1 if analysis['type'] == 'geometry' else self.other_count
                            analysis['should_keep'] = True

                        logger.info(f"  → 类型: {analysis['type']}, 置信度: {analysis['confidence']}, 保留: {analysis['should_keep']}")

                        return analysis
                    else:
                        logger.warning(f"API响应中没有找到message内容")
                        return self._default_result('无有效响应', True)
                else:
                    logger.warning(f"API响应格式异常: {result.keys()}")
                    return self._default_result('响应格式错误', True)
            else:
                logger.warning(f"API调用失败: {response.status_code}, {response.text}")
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
        return {
            'total_analyzed': self.analysis_count,
            'math_formulas': self.math_formula_count,
            'geometry': self.geometry_count,
            'others': self.other_count
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

