"""
DeepSeek AI客户端
用于生成文章摘要、配图提示词等
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

        # 检测是否使用新 V4 模型（默认开启思考模式）
        self.is_v4_model = "deepseek-v4" in self.model
        # 检测是否使用旧推理模型（即将弃用）
        self.is_legacy_reasoner = "reasoner" in self.model

        # 确定轻量级模型（用于简单任务：摘要、配图提示词）
        # 如果当前配置是 pro，则 flash 用作轻量任务
        # 如果当前配置是 flash，则所有任务都用 flash
        if "deepseek-v4-pro" in self.model:
            self.flash_model = "deepseek-v4-flash"
        elif "deepseek-v4-flash" in self.model:
            self.flash_model = self.model  # 已经是 flash，就用配置的模型
        else:
            # 旧模型或其他模型，不使用 flash
            self.flash_model = None

        logger.info(
            f"DeepSeek客户端初始化完成，"
            f"主模型: {self.model}, "
            f"轻量模型: {self.flash_model or '未配置'} "
            f"(V4模型: {self.is_v4_model}, 旧推理模型: {self.is_legacy_reasoner})"
        )

    def _extract_reasoner_content(self, response: str) -> str:
        """
        从旧推理模型（deepseek-reasoner）的响应中提取最终答案

        注意：此方法仅用于旧推理模型（已弃用）
        V4 模型的思考内容已自动隔离，无需提取

        Args:
            response: API响应，可能包含<thinking>标签（仅旧模型）

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
                # 使用轻量级 flash 模型生成摘要（简单任务）
                response = self._call_api(prompt, use_flash=True)

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

    def refine_content(self, content: str, chart_requirements: List[Dict] = None) -> str:
        """
        优化文章内容，并在合适位置插入图片占位符（区分类型）

        Args:
            content: 原始内容
            chart_requirements: 图表需求列表（可选）
                [
                    {
                        "description": "图表描述",
                        "chart_type": "bar|line|pie",
                        "position": "插入位置说明",
                        "has_data": bool,
                        "data_hint": "数据提示"
                    }
                ]

        Returns:
            str: 优化后的内容（包含分类占位符）
        """
        logger.info("开始优化文章内容")

        # 构建图表占位符提示
        chart_placeholder_hint = ""
        if chart_requirements:
            chart_descriptions = []
            for i, req in enumerate(chart_requirements, 1):
                desc = req.get("description", "")
                chart_type = req.get("chart_type", "bar")
                position_hint = req.get("position", "")
                data_hint = req.get("data_hint", "")

                placeholder = f"[[CHART:{desc}]]"
                hint = f"- 需求{i}: {placeholder}\n  类型: {chart_type}\n  建议位置: {position_hint}"
                if data_hint:
                    hint += f"\n  数据提示: {data_hint}"
                chart_descriptions.append(hint)

            chart_placeholder_hint = "\n【数据图表 - CHART】（必须插入）\n"
            chart_placeholder_hint += "以下图表必须在优化后的内容中插入到合适位置：\n\n"
            chart_placeholder_hint += "\n".join(chart_descriptions)
            chart_placeholder_hint += "\n\n⚠️ 重要：这些图表是必须的，请务必在合适位置插入！"

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

在能帮助读者理解的地方，插入以下占位符：

【概念插图 - IMAGE】
用途：视觉隐喻、场景示意、概念解释
⚠️ 重要：插图是纯视觉符号，不要包含任何文字、标签、标题！
格式：[[IMAGE:纯视觉符号描述，不要文字]]
示例：
  * [[IMAGE:左侧传统矿机深灰色，右侧节能设备蓝色渐变，对比图]]
  * [[IMAGE:十字路口路标，两条道路分叉，简洁示意图]]
  * [[IMAGE:抽象的比特币符号半透明化，视觉符号]]

【数据图表 - CHART】
用途：展示精确数据、趋势对比、占比分布
格式：[[CHART:图表描述]]
示例：
  * [[CHART:2020-2024年中国新能源汽车销量增长趋势]]
  * [[CHART:不同品牌的市场份额对比]]

{chart_placeholder_hint}

【插入原则】：
- 只在**有帮助**的地方插入，不是越多越好
- 一篇建议2-4张图片总数（包括插图和图表）
- 占位符单独成行，前后各空一行

【插入位置限制 - 重要】：
- ⚠️ **绝对不要在正文第一个段落之前插入任何图片占位符**
- ⚠️ **封面图已经显示在文章顶部，正文开头不要再插入图片**
- ⚠️ **第一张图片必须在第一个段落内容之后插入**
- 💡 正确做法：让读者先阅读第一段文字，然后再看到第一张插图
- 💡 建议：在第二段或第三段之后再考虑插入第一张图片

【错误示例】：
❌ 第一段内容
[[IMAGE:插图]]  ← 错误：不要在第一段之前插入

【正确示例】：
✅ 第一段内容

第二段内容

[[IMAGE:插图]]  ← 正确：在展开论述后插入

【保留原文占位符】：
如果原文已有占位符，必须保留！
  * 原文：[[IMAGE:描述]] → 保留不变
  * 原文：[[CHART:描述]] → 保留不变

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

            # 如果提供了图表需求，检查是否插入了对应数量的图表
            if chart_requirements:
                expected_charts = len(chart_requirements)
                if chart_count < expected_charts:
                    logger.warning(
                        f"⚠️  预期插入 {expected_charts} 个图表，实际只插入 {chart_count} 个"
                    )

            return response

        except Exception as e:
            logger.error(f"内容优化失败: {e}")
            return content  # 失败时返回原文

    def analyze_chart_requirements(self, content: str, title: str) -> Dict:
        """
        分析文章是否需要生成图表

        Args:
            content: 文章内容
            title: 文章标题

        Returns:
            dict: 图表需求分析结果
                {
                    "needs_charts": bool,  # 是否需要生成图表
                    "requirements": [     # 图表需求列表
                        {
                            "description": "图表描述",
                            "chart_type": "bar|line|pie",
                            "position": "插入位置说明",
                            "has_data": bool,  # 文章是否包含所需数据
                            "data_hint": "数据提示（如果有）"
                        }
                    ]
                }
        """
        logger.info("开始分析图表需求...")

        prompt = f"""请分析以下文章是否需要生成数据图表来增强说明效果。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 图表需求分析任务
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【判断标准】：
1. 是否包含可以量化的数据（趋势、对比、占比等）
2. 是否适合用图表可视化（折线图、柱状图、饼图）
3. 图表是否能帮助读者更好理解内容

【图表类型选择】：
- 折线图 (line)：时间序列变化、趋势走向
- 柱状图 (bar)：数量对比、并列数据
- 饼图 (pie)：占比分布、百分比构成

【返回格式】：
请以JSON格式返回：
{{
  "needs_charts": true/false,
  "requirements": [
    {{
      "description": "图表的简短描述（用于数据搜索）",
      "chart_type": "bar/line/pie",
      "position": "建议插入位置的上下文说明",
      "has_data": true/false,
      "data_hint": "如果文章中有数据，简要说明数据位置和内容"
    }}
  ]
}}

【重要】：
- needs_charts=false 时，requirements 为空数组
- 每篇文章最多建议 2-3 个图表
- 只在真正能增强理解的地方建议图表
- 如果文章中没有明确数据，设置 has_data=false

文章标题：{title}

文章内容：
{content[:3000]}

返回JSON："""

        try:
            response = self._call_api(prompt)

            # 解析JSON响应
            try:
                json_str = self._extract_json_from_markdown(response)
                result = json.loads(json_str)

                needs_charts = result.get("needs_charts", False)
                requirements = result.get("requirements", [])

                logger.info(
                    f"图表需求分析完成: 需要图表={needs_charts}, "
                    f"需求数量={len(requirements)}"
                )

                if needs_charts and requirements:
                    logger.debug("图表需求详情：")
                    for i, req in enumerate(requirements, 1):
                        logger.debug(f"  需求{i}:")
                        logger.debug(f"    描述: {req.get('description')}")
                        logger.debug(f"    类型: {req.get('chart_type')}")
                        logger.debug(f"    包含数据: {req.get('has_data')}")

                return result

            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}, 响应: {response}")
                return {"needs_charts": False, "requirements": []}

        except Exception as e:
            logger.error(f"图表需求分析失败: {e}")
            return {"needs_charts": False, "requirements": []}

    def extract_image_placeholders(self, content: str) -> Dict[str, List[str]]:
        """
        从内容中提取图片占位符

        Args:
            content: 包含占位符的内容

        Returns:
            Dict[str, List[str]]: 分类后的占位符描述
                {
                    "images": ["插图1描述", "插图2描述", ...],   # IMAGE占位符
                    "charts": ["图表1描述", "图表2描述", ...]    # CHART占位符
                }
        """
        import re

        # 提取IMAGE占位符：[[IMAGE:描述]]
        image_pattern = r'\[\[IMAGE:([^\]]+)\]\]'
        image_matches = re.findall(image_pattern, content)

        # 提取CHART占位符：[[CHART:描述]]
        chart_pattern = r'\[\[CHART:([^\]]+)\]\]'
        chart_matches = re.findall(chart_pattern, content)

        result = {
            "images": image_matches,
            "charts": chart_matches
        }

        total_count = len(image_matches) + len(chart_matches)

        if total_count > 0:
            logger.info(
                f"从内容中提取到 {total_count} 个占位符 "
                f"({len(image_matches)}个插图 + {len(chart_matches)}个图表)"
            )

            if image_matches:
                logger.debug("概念插图占位符：")
                for i, desc in enumerate(image_matches, 1):
                    logger.debug(f"  IMAGE{i}: {desc}")

            if chart_matches:
                logger.debug("数据图表占位符：")
                for i, desc in enumerate(chart_matches, 1):
                    logger.debug(f"  CHART{i}: {desc}")
        else:
            logger.info("未检测到任何占位符")

        return result

    def _call_api(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        use_flash: bool = False,
    ) -> str:
        """
        调用DeepSeek API

        Args:
            prompt: 提示词
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            model: 指定使用的模型（可选，覆盖默认模型）
            use_flash: 是否使用轻量级flash模型（仅V4模型支持）

        Returns:
            str: API响应内容
        """
        try:
            # 确定使用的模型
            if model:
                # 显式指定模型
                actual_model = model
            elif use_flash and self.flash_model:
                # 使用轻量级flash模型（用于简单任务）
                actual_model = self.flash_model
            else:
                # 使用默认模型
                actual_model = self.model

            # 构建请求参数
            request_params = {
                "model": actual_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的深度科技内容创作者，擅长为微信公众号撰写高质量的技术洞察文章。你的风格特点是：洞察深刻、启发思考、不说教。目标读者是科技从业者和专业投资者，不是泛流量用户。"
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            # V4 模型默认开启思考模式
            # flash 模型也支持思考模式，可以降低推理强度
            if "deepseek-v4" in actual_model:
                # 根据是否为 flash 模型调整思考强度
                reasoning_effort = "high" if "pro" in actual_model else "enabled"
                request_params["extra_body"] = {
                    "thinking": {
                        "type": "enabled",
                        "reasoning_effort": reasoning_effort
                    }
                }

            response = self.client.chat.completions.create(**request_params)

            raw_content = response.choices[0].message.content.strip()

            # V4 模型和旧推理模型的响应处理方式不同
            # V4 模型：思考内容通常在单独的字段中，不会污染 content
            # 旧推理模型：思考内容在 <thinking> 标签中
            if self.is_legacy_reasoner or ("reasoner" in actual_model):
                # 旧推理模型：提取 <thinking> 标签后的内容
                final_content = self._extract_reasoner_content(raw_content)
                logger.debug(f"旧推理模型响应已处理，原始长度: {len(raw_content)}, 提取后: {len(final_content)}")
                return final_content
            else:
                # V4 模型：直接返回 content（思考内容不在 content 中）
                return raw_content

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise


# 创建全局实例
deepseek_client = DeepSeekClient()
