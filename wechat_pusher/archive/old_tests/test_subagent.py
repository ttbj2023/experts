"""
测试chart-data-researcher subagent
"""
import sys
import os

# 确保在正确的目录
os.chdir('/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

print("=" * 80)
print("测试chart-data-researcher subagent")
print("=" * 80)

# 检查subagent文件是否存在
subagent_path = ".claude/agents/chart-data-researcher.md"
if os.path.exists(subagent_path):
    print(f"✅ Subagent文件存在: {subagent_path}")

    with open(subagent_path, 'r') as f:
        content = f.read()
        print(f"   文件大小: {len(content)} 字节")
        print(f"   包含 'name:': {'name:' in content}")
        print(f"   包含 'description:': {'description:' in content}")
        print(f"   包含 'mcpServers:': {'mcpServers:' in content}")
else:
    print(f"❌ Subagent文件不存在: {subagent_path}")
    sys.exit(1)

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
print("\n请使用以下命令调用subagent:")
print("  Use the chart-data-researcher subagent to find data for: [图表描述]")
print("\n或者直接提供图表占位符:")
print("  [[CHART:柱状图，显示比特币挖矿可再生能源占比（2019-2024）]]")
