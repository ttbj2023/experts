#!/usr/bin/env python3
import re

# 完整的后处理逻辑
def post_process(content):
    # 1. 删除 <thinkcont>...</thinkcont> 标签及其所有内容
    content = re.sub(r'<thinkcont>.*?</thinkcont>', '', content, flags=re.DOTALL)
    
    # 2. 删除其他think标签（保留内容）
    content = re.sub(r'<\|beginofthink\|>', '', content)
    content = re.sub(r'<\|endofthink\|>', '', content)
    content = re.sub(r'</think>
