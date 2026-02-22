# Chart Data Researcher Subagent 使用指南

## 概述

`chart-data-researcher` 是一个专门为图表生成查找准确数值数据的 subagent。它解决了文章需要数据图表但缺乏具体数值的问题。

## Subagent 配置

**文件位置**: `.claude/agents/chart-data-researcher.md`

**功能**:
- 从可靠来源查找精确的数值数据
- 返回结构化的 JSON 格式数据
- 提供数据来源和验证信息
- 专注于加密货币、能源、技术趋势和金融统计

**可用工具**:
- `mcp__tool_engine_local__research_assistant` - 研究助手工具
- `tool-engine-local` MCP 服务器

## 工作流程

### 1. 在 Claude Code 中使用

当你的文章包含类似以下的占位符时：

```markdown
[[CHART:折线图，横轴为年份（2019-2024），纵轴为占比（%）。显示比特币挖矿中可再生能源占比的变化趋势]]
```

你可以这样调用 subagent：

```
Use the chart-data-researcher subagent to find data for the chart described in the article
```

或者更具体地：

```
Use chart-data-researcher to find numerical data for: 折线图，显示比特币挖矿中可再生能源占比（2019-2024）
```

### 2. Subagent 返回的数据格式

成功的响应：

```json
{
  "found": true,
  "chart_data": {
    "type": "line",
    "title": "比特币挖矿可再生能源占比（2019-2024）",
    "labels": ["2019", "2020", "2021", "2022", "2023", "2024"],
    "values": [74.1, 41.15, 28.48, 58.9, 59.9, 56.2],
    "xlabel": "年份",
    "ylabel": "可再生能源占比 (%)"
  },
  "source": "Coinshares, 剑桥大学替代金融中心 (CCAF), 比特币矿业委员会 (BMC)",
  "notes": "数据说明：..."
}
```

失败的响应：

```json
{
  "found": false,
  "reason": "无法找到该主题的精确数值数据",
  "suggestions": ["尝试使用相关关键词", "扩大时间范围"]
}
```

### 3. 集成到工作流

在 Python 代码中（当前未完全集成）：

```python
from src.workflow.publisher import ArticlePublisher

publisher = ArticlePublisher()

# 当前：_research_chart_data 返回 None，使用默认配置
# 未来：将集成 research_assistant 调用

ai_result = publisher.analyze_with_ai(article)
images = publisher.generate_images(ai_result, article_id)
```

## 数据质量保证

Subagent 遵循以下原则：

1. **数据准确性优先**: 从不编造或估算数值
2. **来源验证**: 提供数据来源和发布日期
3. **结构化输出**: 一致的 JSON 格式便于解析
4. **明确说明缺口**: 如果数据不完整，明确标注

## 支持的数据类型

- **时间序列数据**: 年度/季度/月度趋势
- **对比数据**: 不同类别的数值对比
- **分布数据**: 百分比占比（总和为 100%）
- **统计指标**: 平均值、中位数、增长率

## 专业领域

Subagent 在以下领域特别擅长：

- **加密货币**: 挖矿统计、能耗、算力、采用率
- **能源**: 可再生能源占比、能耗趋势、成本对比
- **技术**: 算力增长、芯片性能、网络统计
- **金融**: 市值、交易量、价格趋势（历史）

## 示例

### 示例 1: 比特币可再生能源占比

**输入**:
```
折线图，横轴为年份（2019-2024），纵轴为占比（%）。
显示比特币挖矿中可再生能源占比的变化趋势
```

**关键词**: `["bitcoin", "renewable energy", "mining", "percentage", "2019-2024"]`

**返回数据**:
```json
{
  "found": true,
  "chart_data": {
    "type": "line",
    "title": "比特币挖矿可再生能源占比",
    "labels": ["2019", "2020", "2021", "2022", "2023", "2024"],
    "values": [74.1, 41.15, 28.48, 58.9, 59.9, 56.2],
    "xlabel": "年份",
    "ylabel": "可再生能源占比 (%)"
  },
  "source": "比特币矿业委员会 (BMC), 剑桥大学 (CCAF)"
}
```

### 示例 2: 比特币算力增长

**输入**:
```
折线图，显示全球比特币算力总量增长趋势（2020-2024，单位：EH/s）
```

**关键词**: `["bitcoin", "hash rate", "EH/s", "network", "2020-2024"]`

**返回数据**:
```json
{
  "found": true,
  "chart_data": {
    "type": "line",
    "title": "比特币网络算力增长",
    "labels": ["2020", "2021", "2022", "2023", "2024"],
    "values": [150, 180, 250, 400, 600],
    "xlabel": "年份",
    "ylabel": "算力 (EH/s)"
  },
  "source": "Blockchain.com, CoinMetrics"
}
```

## 当前限制

1. **Python 集成待完成**: `publisher._research_chart_data()` 方法目前返回 `None`
2. **手动调用**: 需要在 Claude Code 中手动调用 subagent
3. **依赖外部工具**: 依赖 `tool_engine_local` 的 `research_assistant`

## 未来计划

1. **完整 Python 集成**: 直接在代码中调用 `research_assistant`
2. **自动检测**: 自动识别需要数据的图表并调用 subagent
3. **缓存机制**: 缓存已查询的数据避免重复调用
4. **数据验证**: 添加数据合理性检查

## 相关文件

- Subagent 配置: `.claude/agents/chart-data-researcher.md`
- Publisher 实现: `src/workflow/publisher.py`
- 图表生成器: `src/chart/chart_generator.py`
- 测试脚本: `test_integrated_workflow.py`

## 快速开始

1. **创建测试文章**:
```bash
python test_integrated_workflow.py
```

2. **在 Claude Code 中使用 subagent**:
```
Use the chart-data-researcher subagent to find data for: [图表描述]
```

3. **查看生成的图表**:
```bash
ls output/test_chart_workflow/
```

## 故障排查

### Subagent 未被识别

- 确保 `.claude/agents/chart-data-researcher.md` 文件存在
- 重启 Claude Code 会话以加载新的 subagent
- 检查 YAML frontmatter 格式是否正确

### Research_assistant 调用失败

- 确认 `tool-engine-local` MCP 服务器已配置
- 检查网络连接
- 查看日志中的详细错误信息

### 数据未找到

- 尝试使用更通用的关键词
- 扩大时间范围
- 检查该领域是否有公开的统计数据

## 最佳实践

1. **明确描述**: 清楚地说明需要的图表类型、时间范围、数据单位
2. **验证数据**: 检查返回数据的合理性（如百分比在 0-100 之间）
3. **记录来源**: 保留数据来源以备后续引用
4. **处理缺口**: 如果数据不完整，考虑使用估算值或说明缺失情况

## 联系与支持

如有问题或建议，请查看：
- 项目 CLAUDE.md
- GitHub issues
- Claude Code 官方文档
