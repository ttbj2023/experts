"""
简单测试：直接调用研究助手
"""
import sys
import json

# 尝试通过MCP客户端调用
try:
    # 方法1：直接从全局导入
    from mcp__tool_engine_local__research_assistant import research_assistant
    print("✅ 成功导入 research_assistant")

    # 测试调用
    print("\n测试调用...")
    result = research_assistant(
        keywords=["bitcoin", "renewable energy", "mining", "2024"],
        requirements="查找比特币挖矿中可再生能源占比的百分比数据（2020-2024年）",
        detail_level="standard"
    )

    print("\n查询结果:")
    print("=" * 80)
    print(result)
    print("=" * 80)

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n尝试查找MCP服务器配置...")

    # 方法2：查找MCP服务器
    import os
    home = os.path.expanduser("~")
    config_paths = [
        f"{home}/.config/claude-code/settings.json",
        f"{home}/.claude/settings.json",
        "./.mcp.json",
    ]

    for path in config_paths:
        if os.path.exists(path):
            print(f"\n找到配置文件: {path}")
            with open(path) as f:
                config = json.load(f)
                print(json.dumps(config, indent=2, ensure_ascii=False)[:500])
                break
    else:
        print("未找到MCP配置文件")

except Exception as e:
    print(f"❌ 调用失败: {e}")
    import traceback
    traceback.print_exc()
