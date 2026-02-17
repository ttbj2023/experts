#!/usr/bin/env python3
"""
测试简化版后处理效果
"""

import re


def simplified_post_process(content: str) -> str:
    """
    简化的后处理：只删除特殊标签，保留内容

    Args:
        content: 原始识别内容

    Returns:
        处理后的内容
    """
    # 1. 删除 <|beginofthink|> 和 <|endofthink|> 标签（保留内容）
    content = re.sub(r'<\|beginofthink\|>', '', content)
    content = re.sub(r'<\|endofthink\|>', '', content)

    # 2. 删除 <|beginofbox|> 和 <|endofbox|> 标签（保留内容）
    content = re.sub(r'<\|beginofbox\|>', '', content)
    content = re.sub(r'<\|endofbox\|>', '', content)

    # 3. 清理首尾空白
    content = content.strip()

    return content


# 测试数据
test_raw_content = """
<|beginofthink|>
用户现在需要识别提供的数学教材页面内容，转换为Markdown格式。

首先看页面的结构，标题、目标直通车、知识点等部分。

需要注意数学公式的正确识别，比如平均数的公式$$\\overline{x} = \\frac{1}{n}(x_1 + x_2 + \\cdots + x_n)$$。
<|endofthink|>

<|beginofbox|>
数学|八年级下
# 24.1 数据的集中趋势

目标直通车
- 理解平均数、中位数和众数等统计量的定义。
- 会计算加权平均数，理解"权"的意义。

## 知识点1 平均数
一般地，有n个数据$x_1,x_2,\dots ,x_n$，我们把$\overline{x}=\frac{1}{n}(x_1+x_2+\cdots +x_n)$叫做这n个数据的平均数。

示例：数据1,0,3,4,4的平均数是（ ）
A. 4
B. 3
C. 2.5
D. 2
<|endofbox|>
"""

# 执行后处理
result = simplified_post_process(test_raw_content)

print("="*60)
print("简化版后处理结果")
print("="*60)
print(result)
print("="*60)
print("\n✅ 说明：")
print("1. <|beginofthink|> 和 <|endofthink|> 标签已删除")
print("2. <|beginofbox|> 和 <|endofbox|> 标签已删除")
print("3. 标签内的内容全部保留")
print("4. 没有其他格式修改（表格、公式等保持原样）")
