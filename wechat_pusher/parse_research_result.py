"""
解析research_assistant返回的数据
"""
import json
import re

# research_assistant返回的结果
result = """根据您的要求，以下是2019年至2024年比特币挖矿中可再生能源占比的具体数值数据，并以JSON格式返回。数据主要来源于比特币矿业委员会（BMC）和剑桥大学替代金融中心（CCAF）的报告。

```json
{
  "source": "Coinshares, 剑桥大学替代金融中心 (CCAF), 比特币矿业委员会 (BMC), Odaily",
  "data": {
    "years": [2019, 2020, 2021, 2022, 2023, 2024],
    "percentages": [74.1, 41.15, 28.48, 58.9, 59.9, 56.2]
  },
  "notes": "数据说明：\\n1. '可再生能源占比' 和 '可持续能源占比'：在比特币挖矿的能源构成中，'可持续能源'通常包括可再生能源（如水电、风能、太阳能）和核能。用户要求提供的是'可再生能源占比'，但在某些年份，主要数据来源仅提供了'可持续能源占比'。在这些情况下，我们使用了可持续能源占比，并在说明中注明。\\n2. 2019年：Coinshares报告指出，截至2019年6月，比特币挖矿有74.1%的可再生能源驱动。\\n3. 2020年：剑桥大学替代金融中心（CCAF）的数据显示，2020年比特币挖矿电力结构中可再生能源的份额为41.15%。\\n4. 2021年：CCAF的数据显示，2021年比特币挖矿电力结构中可再生能源的份额下降至28.48%。 值得注意的是，比特币矿业委员会（BMC）在2021年第四季度估算全球挖矿行业的可持续电力组合已增长至约58.5%。 这种差异可能源于不同的调查方法和对'可再生'与'可持续'（包含核能）的定义。\\n5. 2022年：比特币矿业委员会（BMC）在2022年第四季度的报告显示，比特币挖矿的可持续能源组合为58.9%。 而CCAF在2022年的报告中指出，可持续能源占比为37.6%。 考虑到用户对BMC数据的偏好，此处采用BMC的数据，并将其标注为可持续能源占比。\\n6. 2023年：比特币矿业委员会（BMC）在2023年上半年的调查结果显示，全球比特币挖矿行业的可持续电力组合为59.9%。\\n7. 2024年：Odaily报道，截至2024年7月，比特币挖矿的可持续能源利用率已达到历史最高水平56.2%。"
}
```
"""

# 提取JSON
json_pattern = r'```json\s*\n?(\{.*?\})\s?```'
match = re.search(json_pattern, result, re.DOTALL)

if match:
    json_str = match.group(1)
    data = json.loads(json_str)

    print("=" * 80)
    print("✅ 成功解析research_assistant返回的数据")
    print("=" * 80)

    print("\n数据来源：")
    print(f"  {data['source']}")

    print("\n数据点：")
    years = data['data']['years']
    percentages = data['data']['percentages']

    for year, pct in zip(years, percentages):
        print(f"  {year}: {pct}%")

    print("\n数据说明（摘要）：")
    notes = data['notes']
    # 只显示前200个字符
    if len(notes) > 200:
        print(f"  {notes[:200]}...")
    else:
        print(f"  {notes}")

    print("\n" + "=" * 80)
    print("✅ 数据格式验证通过")
    print("=" * 80)

    print("\n这个数据可以用于生成:")
    print("  - 图表类型: 折线图 (line)")
    print(f"  - X轴: 年份 (2019-{years[-1]})")
    print("  - Y轴: 可再生能源占比 (%)")
    print(f"  - 数据点: {len(years)}个")

else:
    print("❌ 无法提取JSON数据")
