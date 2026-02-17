"""
GLM-4.6V-Flash 客户端

统一的GLM API调用接口，支持：
1. OCR识别 - 将PDF页面转换为Markdown
2. 图片描述 - 生成图片的详细描述
"""

import base64
import io
import re
from typing import Dict, Optional
from PIL import Image
import requests


class GLMClient:
    """GLM-4.6V-Flash API客户端"""

    def __init__(self, config: Dict):
        """
        初始化GLM客户端

        Args:
            config: 配置字典，从config/default.yaml加载
        """
        self.api_url = config['models']['glm']['api_url']
        self.model = config['models']['glm']['model']
        self.max_tokens = config['models']['glm']['max_tokens']
        self.timeout = config['models']['glm']['timeout']
        self.temperature = config['models']['glm']['temperature']
        self.api_key = config.get('glm_api_key', '')

    # ========================================
    # 公共方法
    # ========================================

    def describe_image(
        self,
        image_path: str,
        max_size: int = 1280,
        prompt: Optional[str] = None
    ) -> str:
        """
        描述图片内容（用于Stage 2/Stage 3图片描述）

        Args:
            image_path: 图片文件路径
            max_size: 图片最大尺寸（长边）
            prompt: 自定义提示词（可选）

        Returns:
            图片描述文本
        """
        if prompt is None:
            prompt = """请详细描述这张图片的内容。

要求：
1. 识别图片的类型（几何图形、数学公式、统计图表、示意图、地图等）
2. 描述图片中的关键元素和细节
3. 如果有文字或标注，请准确引用
4. 描述要准确、简洁，不超过200字

请直接返回描述文本，不要添加其他内容。"""

        # 压缩图片
        base64_image = self._compress_image(image_path, max_size)

        # 调用API
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": self.temperature
        }

        result = self._call_api(payload, timeout=60)

        # 清理think标签
        description = self._clean_think_tags(result.get('content', ''))

        return description.strip()

    def ocr_page(
        self,
        image_path: str,
        prompt: Optional[str] = None,
        max_tokens: int = 8192
    ) -> str:
        """
        OCR识别PDF页面（用于Stage 1 OCR识别）

        Args:
            image_path: 页面图片路径
            prompt: 自定义OCR提示词（可选）
            max_tokens: 最大输出token数

        Returns:
            识别的Markdown内容
        """
        if prompt is None:
            prompt = """你是一个专业的OCR识别系统。请将这个PDF页面转换为Markdown格式。

## 输出格式要求
请使用以下格式输出：
```markdown
[你的Markdown内容]
```

## 转换规则

### 文字内容
- 标题：使用 # ## ### #### 表示层级
- 段落：直接输出文字，空行分隔
- 列表：使用 - 或 1.
- 表格：使用 Markdown表格语法
- 公式：行内用 $x^2$，独立用 $$\\frac{a}{b}$$

### 图片处理（严格遵守格式！）

遇到图片时使用以下**精确的HTML注释格式**（不要使用Markdown图片语法）：

```html
<!-- IMAGE_PLACEHOLDER
type: <图片类型，如：几何图形、统计图表、示意图等>
description: <详细描述图片内容，包括所有可见的文本、标注、数据、颜色、位置等关键信息>
-->
```

⚠️ **重要提醒**：
1. 必须使用上述HTML注释格式 `<!-- ... -->`
2. **不要使用** `![图片描述](IMAGE_PLACEHOLDER)` 格式
3. 占位符单独占一行，前后各空一行

#### 占位符示例：

**示例1 - 几何图形：**
```html
<!-- IMAGE_PLACEHOLDER
type: 几何图形
description: 三角形ABC，顶点A在上方，B在左下角，C在右下角，边AB=5cm，BC上有点D
-->
```

**示例2 - 统计图表：**
```html
<!-- IMAGE_PLACEHOLDER
type: 统计图表
description: 柱状图，横轴显示2020-2024年，纵轴显示销售额（万元），数据分别为120、150、180、200、250
-->
```

**示例3 - 示意图：**
```html
<!-- IMAGE_PLACEHOLDER
type: 示意图
description: 流程图，从上到下依次为：开始 → 输入数据 → 处理 → 输出结果 → 结束
-->
```

### 页眉页脚处理 ⚠️ 重要
- **不要识别页眉页脚**：忽略页面顶部和底部的重复信息（如书名、章节号、页码等）
- **只识别正文内容**：专注于页面中间的主要内容区域
- 常见页眉页脚特征：
  * 页码："1"、"第1页"、"Page 1"、"- 1 -"等
  * 书名/章节：出现在每页顶部或底部的重复标题
  * 装饰线：上下边框线、分隔线等

### 质量要求
1. 不要遗漏任何文字或图片
2. 保持原文的逻辑顺序
3. 专业术语、数字、符号必须准确
4. 图片描述要详细具体"""

        # 压缩图片
        base64_image = self._compress_image(image_path, compression='medium')

        # 调用API
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature
        }

        result = self._call_api(payload, timeout=self.timeout)

        # 清理think标签并提取Markdown
        markdown = self._clean_think_tags(result.get('content', ''))
        markdown = self._extract_markdown_content(markdown)

        return markdown

    # ========================================
    # 私有方法
    # ========================================

    def _compress_image(
        self,
        image_path: str,
        max_size: int = 1280,
        compression: str = 'medium'
    ) -> str:
        """
        压缩图片并转换为base64

        Args:
            image_path: 图片路径
            max_size: 最大尺寸（长边）
            compression: 压缩级别 (low/medium/high)

        Returns:
            base64编码的图片字符串
        """
        # 确定JPEG质量
        quality_map = {
            'low': 95,
            'medium': 85,
            'high': 75
        }
        quality = quality_map.get(compression, 85)

        # 打开并压缩图片
        img = Image.open(image_path)
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # 转换图片模式以支持JPEG格式
        if img.mode == 'RGBA':
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
            img = background
        elif img.mode not in ('RGB', 'L'):
            # 其他模式转换为RGB
            img = img.convert('RGB')

        # 转换为JPEG字节流
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        image_bytes = buffer.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        return base64_image

    def _call_api(self, payload: Dict, timeout: int = 60) -> Dict:
        """
        调用GLM-4.6V-Flash API

        Args:
            payload: API请求体
            timeout: 超时时间（秒）

        Returns:
            API响应内容

        Raises:
            requests.HTTPError: API调用失败
        """
        headers = {
            "Content-Type": "application/json"
        }

        # 如果有API key，添加到headers
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(
            f"{self.api_url}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )

        response.raise_for_status()
        result = response.json()

        # 提取content
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        return {'content': content, 'raw': result}

    def _clean_think_tags(self, content: str) -> str:
        """
        清理GLM-4.6V-Flash返回的think标签

        Args:
            content: 原始内容

        Returns:
            清理后的内容
        """
        # 移除think标签及其内容
        content = re.sub(r'<\|think\|>.*?<\|/think\|>', '', content, flags=re.DOTALL)

        # 清理多余空白
        content = content.strip()

        return content

    def _extract_markdown_content(self, content: str) -> str:
        """
        从内容中提取Markdown代码块

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
