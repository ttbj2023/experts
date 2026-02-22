"""
DeepSeek AI客户端
用于生成文章摘要、图表提示词、配图提示词等
"""
import json
from typing import Dict, List, Optional
from openai import OpenAI

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DeepSeekClient:
    """DeepSeek AI客户端"""

    def __init__(self):
        """初始化客户端"""
        self.client = OpenAI(
            api_key=config.deepseek.api_key,
            base_url=config.deepseek.base_url,
        )
        self.model = config.deepseek.model
        self.max_tokens = config.deepseek.max_tokens
        self.temperature = config.deepseek.temperature

        # 检测是否使用推理模型
        self.is_reasoner = "reasoner" in self.model

        logger.info(f"DeepSeek客户端初始化完成，模型: {self.model} (推理模式: {self.is_reasoner})")

    def _extract_reasoner_content(self, response: str) -> str:
        """
        从推理模型的响应中提取最终答案

        Args:
            response: API响应，可能包含<thinking>标签

        Returns:
            提取出的最终答案内容
        """
        # 查找 <thinking> 标签
        thinking_start = response.find("<thinking>")
        if thinking_start == -1:
            # 没有 thinking 标签，直接返回
            return response.strip()

        # 查找 </thinking> 结束标签
        thinking_end = response.find("</thinking>")
        if thinking_end == -1:
            # 只有开始标签，返回之后的所有内容
            final_answer = response[thinking_start + len("<thinking>"):].strip()
        else:
            # 返回 thinking 标签之后的内容
            final_answer = response[thinking_end + len("</thinking>"):].strip()

        return final_answer

    def _extract_json_from_markdown(self, response: str) -> str:
        """
        从markdown代码块中提取JSON内容

        Args:
            response: API响应，可能包含markdown代码块

        Returns:
            纯净的JSON字符串
        """
        import re

        # 尝试提取 ```json ... ``` 或 ``` ... ``` 代码块
        pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        match = re.search(pattern, response, re.DOTALL)

        if match:
            json_content = match.group(1).strip()
            logger.debug("从markdown代码块中提取JSON")
            return json_content

        # 如果没有代码块，返回原始内容
        return response.strip()

    def generate_summary(self, content: str, max_length: int = 50, max_retries: int = 3) -> str:
        """
        生成文章摘要

        Args:
            content: 文章内容
            max_length: 摘要目标字数（默认50字，仅用于提示词）
            max_retries: 超过120字符硬限制时最大重试次数（默认3次）

        Returns:
            str: 生成的摘要
        """
        logger.info("开始生成文章摘要")

        # 微信公众号摘要硬限制（中文、英文、标点都算1个字符）
        WECHAT_MAX_CHARS = 120

        for attempt in range(max_retries):
            # 根据尝试次数调整提示词的严格程度
            if attempt == 0:
                length_instruction = f"严格控制在{max_length}字以内"
            elif attempt == 1:
                length_instruction = f"绝对不能超过120字符！这是第一次超长，请务必精简！"
            else:
                length_instruction = f"紧急：已经超长{attempt}次！必须在120字符以内，删除所有次要信息！"

            prompt = f"""请为以下文章生成一个简洁的摘要，要求：
1. 长度严格控制在{max_length}字以内（{length_instruction}）
2. 概括文章核心洞察和关键观点
3. 体现深度思考，避免泛泛而谈
4. 语言精炼，符合"洞察、启发、不说教"的风格
5. 不要添加"本文介绍了"等冗余词语，直接给出摘要内容

文章内容：
{content[:2000]}

摘要（{max_length}字以内）："""

            try:
                response = self._call_api(prompt)

                # 检查字符数（微信按字符统计：汉字、字母、标点都算1个字符）
                char_count = len(response)

                # 只要不超过120字符硬限制就接受，只有超过才重试
                if char_count <= WECHAT_MAX_CHARS:
                    logger.info(f"摘要生成成功，长度: {char_count}字符")
                    return response
                else:
                    # 超过120字符硬限制，记录并重试
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"摘要超过微信硬限制（{char_count}字符 > {WECHAT_MAX_CHARS}），"
                            f"第{attempt + 1}次重试..."
                        )
                    else:
                        # 最后一次尝试也超长，返回空字符串
                        logger.error(
                            f"摘要生成{max_retries}次后仍超过微信硬限制({char_count}字符)，放弃生成。"
                        )
                        return ""  # 不进行截断，返回空字符串

            except Exception as e:
                logger.error(f"摘要生成失败: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return ""

        return ""

    def generate_chart_prompt(self, content: str) -> Optional[Dict[str, any]]:
        """
        生成图表提示词和数据

        Args:
            content: 文章内容

        Returns:
            dict: 包含图表类型、标题、数据的字典，如果没有需要可视化的数据则返回None
        """
        logger.info("开始生成图表提示词")

        prompt = f"""分析以下文章内容，判断是否需要生成数据图表。

文章定位：深度科技洞察，面向专业读者，强调"洞察、启发、不说教"的风格。

如果需要，请以JSON格式返回，格式如下：
{{
  "need_chart": true,
  "chart_type": "bar|line|pie",
  "title": "图表标题",
  "data": {{
    "labels": ["标签1", "标签2", "标签3"],
    "values": [10, 20, 30],
    "xlabel": "X轴标签",
    "ylabel": "Y轴标签"
  }},
  "description": "图表说明文字"
}}

如果不需要数据可视化，返回：
{{
  "need_chart": false,
  "reason": "不需要图表的原因"
}}

文章内容：
{content[:3000]}

返回JSON："""

        try:
            response = self._call_api(prompt, temperature=0.3)  # 降低温度以获得更确定的结果

            # 解析JSON响应
            try:
                # 尝试从markdown代码块中提取JSON
                json_str = self._extract_json_from_markdown(response)
                result = json.loads(json_str)

                if result.get("need_chart"):
                    logger.info(f"需要生成图表，类型: {result.get('chart_type')}")
                    return result
                else:
                    logger.info(f"不需要生成图表: {result.get('reason')}")
                    return None

            except json.JSONDecodeError:
                logger.error(f"JSON解析失败: {response}")
                return None

        except Exception as e:
            logger.error(f"图表提示词生成失败: {e}")
            return None

    def generate_image_prompts(
        self, content: str, title: str
    ) -> Dict[str, List[str]]:
        """
        生成配图提示词（封面图和插图）

        Args:
            content: 文章内容
            title: 文章标题

        Returns:
            dict: 包含cover_prompts（封面图提示词）和image_prompts（插图提示词）的字典
        """
        logger.info("开始生成配图提示词")

        prompt = f"""根据以下文章内容，生成配图提示词。

文章定位：深度科技洞察，面向专业读者，强调"洞察、启发、不说教"的风格。
目标受众：科技从业者、投资者、技术爱好者，不是泛流量读者。

请以JSON格式返回，格式如下：
{{
  "cover_prompts": [
    "封面图描述，要求：16:9比例，体现深度科技洞察风格..."
  ],
  "image_prompts": [
    "插图1描述，要求：风格、内容、色彩...",
    "插图2描述",
    "插图3描述",
    "插图4描述"
  ],
  "style": "整体视觉风格描述",
  "color_scheme": "色彩方案建议"
}}

要求：
1. 封面图：1个描述，要求体现文章核心洞察，有深度感，避免花哨
2. 插图：3-4个描述，辅助理解文章观点，简洁专业
3. 风格要求：专业、克制、有质感，符合深度科技定位
4. 视觉元素：避免过于抢眼的色彩，注重留白和意境
5. 不做流量导向：不使用夸张、猎奇、标题党式的视觉元素
6. **严禁文字**：图片中不要包含任何文字、标题、标签等文本元素
7. **纯净描述**：不要在提示词中提及"微信文章封面"、"封面图"等平台特定词汇，只描述画面内容

文章标题：{title}

文章内容：
{content[:3000]}

返回JSON："""

        try:
            response = self._call_api(prompt)

            # 解析JSON响应
            try:
                # 尝试从markdown代码块中提取JSON
                json_str = self._extract_json_from_markdown(response)
                result = json.loads(json_str)

                logger.info(
                    f"配图提示词生成成功: "
                    f"{len(result.get('cover_prompts', []))}个封面提示, "
                    f"{len(result.get('image_prompts', []))}个插图提示"
                )

                return result

            except json.JSONDecodeError:
                logger.error(f"JSON解析失败: {response}")
                return {"cover_prompts": [], "image_prompts": []}

        except Exception as e:
            logger.error(f"配图提示词生成失败: {e}")
            return {"cover_prompts": [], "image_prompts": []}

    def refine_content(self, content: str) -> str:
        """
        优化文章内容，并在合适位置插入图片占位符（区分类型）

        Args:
            content: 原始内容

        Returns:
            str: 优化后的内容（包含分类占位符）
        """
        logger.info("开始优化文章内容")

        prompt = f"""请优化以下文章内容，使其更适合在微信公众号发布。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 主要任务：文章内容优化
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

文章定位：深度科技洞察，面向专业读者，强调"洞察、启发、不说教"的风格。

【优化重点】（按优先级排序）：
1. ✅ 保持核心洞察：不改变原文的深度思考和观点
2. ✅ 移动端适配：调整段落长度，但避免过度碎片化（3-5句一段）
3. ✅ 语言风格：克制、专业、有深度，避免说教和煽动
4. ✅ 结构优化：添加必要的小标题，提升可读性
5. ✅ 避免流量化：不制造焦虑、不用标题党语言
6. ✅ 格式规范：保持Markdown格式

【微信阅读习惯】：
- 段落：3-5句话为一段，不超过150字
- 标题：用二级/三级标题分隔章节
- 重点：用粗体强调关键信息，但不要过度使用
- 列表：用列表展示要点，提升扫读效率

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 次要任务：插入图片占位符（辅助理解）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

在能帮助读者理解的地方，插入以下两种占位符：

【类型1：数据图表 - CHART】
用途：精确数值对比、时间趋势、占比分布
格式：[[CHART:图表类型，坐标轴说明，数据（如果有）]]
示例：
  * [[CHART:柱状图，横轴年份2020-2024，纵轴能耗数值，对比传统和可再生能源挖矿]]
  * [[CHART:折线图，横轴时间2019-2024，纵轴可再生能源占比%]]

【类型2：概念插图 - IMAGE】
用途：视觉隐喻、场景示意、概念解释
⚠️ 重要：插图是纯视觉符号，不要包含任何文字、标签、标题！
格式：[[IMAGE:纯视觉符号描述，不要文字]]
示例：
  * [[IMAGE:左侧传统矿机深灰色，右侧节能设备蓝色渐变，对比图]]
  * [[IMAGE:十字路口路标，两条道路分叉，简洁示意图]]
  * [[IMAGE:抽象的比特币符号半透明化，视觉符号]]

【插入原则】：
- 只在**有帮助**的地方插入，不是越多越好
- 有数据对比用CHART，概念解释用IMAGE
- 一篇建议2-4张图片总数
- 占位符单独成行，前后各空一行

【保留原文占位符】：
如果原文已有占位符（特别是包含数据的），必须保留！
  * 原文：[[CHART:柱状图，数据：A: 10%, B: 20%]] → 保留不变
  * 原文：[[CHART:折线图，从6%调整到9%]] → 保留不变

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

原文内容：
{content}

优化后的内容："""

        try:
            response = self._call_api(prompt)

            # 验证占位符格式
            import re
            chart_count = len(re.findall(r'\[\[CHART:[^\]]+\]\]', response))
            image_count = len(re.findall(r'\[\[IMAGE:[^\]]+\]\]', response))
            total_count = chart_count + image_count

            logger.info(
                f"内容优化成功，检测到 {total_count} 个占位符 "
                f"({chart_count}个数据图表 + {image_count}个概念插图)"
            )

            return response

        except Exception as e:
            logger.error(f"内容优化失败: {e}")
            return content  # 失败时返回原文

    def extract_image_placeholders(self, content: str) -> Dict[str, List[str]]:
        """
        从内容中提取并分类图片占位符

        Args:
            content: 包含占位符的内容

        Returns:
            Dict[str, List[str]]: 分类后的占位符描述
                {
                    "charts": ["图表1描述", "图表2描述", ...],  # CHART占位符
                    "images": ["插图1描述", "插图2描述", ...]   # IMAGE占位符
                }
        """
        import re

        # 提取CHART占位符：[[CHART:描述]]
        chart_pattern = r'\[\[CHART:([^\]]+)\]\]'
        chart_matches = re.findall(chart_pattern, content)

        # 提取IMAGE占位符：[[IMAGE:描述]]
        image_pattern = r'\[\[IMAGE:([^\]]+)\]\]'
        image_matches = re.findall(image_pattern, content)

        result = {
            "charts": chart_matches,
            "images": image_matches
        }

        total_count = len(chart_matches) + len(image_matches)

        if total_count > 0:
            logger.info(
                f"从内容中提取到 {total_count} 个占位符 "
                f"({len(chart_matches)}个数据图表 + {len(image_matches)}个概念插图)"
            )

            if chart_matches:
                logger.debug("数据图表占位符：")
                for i, desc in enumerate(chart_matches, 1):
                    logger.debug(f"  CHART{i}: {desc}")

            if image_matches:
                logger.debug("概念插图占位符：")
                for i, desc in enumerate(image_matches, 1):
                    logger.debug(f"  IMAGE{i}: {desc}")
        else:
            logger.info("未检测到任何占位符")

        return result

    def _call_api(
        self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None
    ) -> str:
        """
        调用DeepSeek API

        Args:
            prompt: 提示词
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）

        Returns:
            str: API响应内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的深度科技内容创作者，擅长为微信公众号撰写高质量的技术洞察文章。你的风格特点是：洞察深刻、启发思考、不说教。目标读者是科技从业者和专业投资者，不是泛流量用户。"
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )

            raw_content = response.choices[0].message.content.strip()

            # 如果是推理模型，提取最终答案（去除思考过程）
            if self.is_reasoner:
                final_content = self._extract_reasoner_content(raw_content)
                logger.debug(f"推理模型响应已处理，原始长度: {len(raw_content)}, 提取后: {len(final_content)}")
                return final_content

            return raw_content

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise


# 创建全局实例
deepseek_client = DeepSeekClient()
