#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from src.utils.markdown_parser import MarkdownParser

# 读取测试文件
with open('test_quick.md', 'r') as f:
    content = f.read()

print(f"Content length: {len(content)}")
print(f"Content:\n{content[:200]}...")

parser = MarkdownParser()

print("\nStarting parse...")
import time
start = time.time()

result = parser.parse(content)

elapsed = time.time() - start
print(f"\nParse completed in {elapsed:.2f} seconds")
print(f"Sections: {len(result['sections'])}")

for i, section in enumerate(result['sections'][:5]):
    print(f"{i+1}. {section.get('type', 'unknown')}: {section.get('content', '')[:50]}...")
