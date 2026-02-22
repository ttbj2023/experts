#!/usr/bin/env python3
"""
下载微信公众号草稿
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.wechat.api_client import WeChatApiClient
from dotenv import load_dotenv

load_dotenv()


def list_drafts(count: int = 20):
    """列出草稿"""
    client = WeChatApiClient()

    # 先获取不包含content的列表（更快）
    print("📋 正在获取草稿列表...")
    result = client.get_draft_list(offset=0, count=count, no_content=1)

    if not result:
        print("❌ 获取草稿列表失败")
        return

    print(f"\n✅ 共有 {result['total_count']} 个草稿：\n")

    for i, draft in enumerate(result['item_list'], 1):
        media_id = draft.get('media_id', '')
        update_time = draft.get('update_time', 0)
        update_time_str = datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S')

        # 获取文章信息
        content = draft.get('content', {})
        news_item = content.get('news_item', [])

        if news_item:
            article = news_item[0]
            title = article.get('title', '无标题')
            author = article.get('author', '未知')
            digest = article.get('digest', '')[:50] + '...' if article.get('digest') else ''

            print(f"{i}. 【{title}】")
            print(f"   作者: {author}")
            print(f"   Media ID: {media_id}")
            print(f"   更新时间: {update_time_str}")
            print(f"   摘要: {digest}")
            print()


def download_draft(media_id: str, output_dir: str = "output/drafts"):
    """下载指定草稿的HTML内容"""
    client = WeChatApiClient()

    print(f"📥 正在下载草稿: {media_id}")

    # 获取包含完整content的草稿列表（分批获取，最多100个）
    target_draft = None
    for offset in [0, 20, 40, 60, 80]:
        result = client.get_draft_list(offset=offset, count=20, no_content=0)

        if not result:
            continue

        # 查找指定的草稿
        for draft in result['item_list']:
            if draft.get('media_id') == media_id:
                target_draft = draft
                break

        if target_draft:
            break

    if not target_draft:
        print(f"❌ 未找到 media_id={media_id} 的草稿")
        return False

    # 获取文章内容
    content = target_draft.get('content', {})
    news_item = content.get('news_item', [])

    if not news_item:
        print("❌ 草稿中没有文章内容")
        return False

    article = news_item[0]
    title = article.get('title', '未命名')
    html_content = article.get('content', '')
    author = article.get('author', '未知')

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 保存HTML文件
    file_name = f"{title}.html"
    # 移除文件名中的非法字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        file_name = file_name.replace(char, '_')

    html_file = output_path / file_name
    html_file.write_text(html_content, encoding='utf-8')

    print(f"✅ 下载成功!")
    print(f"   标题: {title}")
    print(f"   作者: {author}")
    print(f"   保存到: {html_file}")

    # 同时保存元数据
    meta_file = html_file.with_suffix('.meta.json')
    meta_data = {
        "title": title,
        "author": author,
        "media_id": media_id,
        "digest": article.get('digest', ''),
        "thumb_media_id": article.get('thumb_media_id', ''),
        "show_cover_pic": article.get('show_cover_pic', 0),
        "url": article.get('url', ''),
        "content_source_url": article.get('content_source_url', ''),
        "update_time": target_draft.get('update_time', 0),
        "html_file": str(html_file)
    }

    meta_file.write_text(json.dumps(meta_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"   元数据: {meta_file}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  列出所有草稿:")
        print("    python download_draft.py list")
        print()
        print("  下载指定草稿:")
        print("    python download_draft.py download <media_id> [输出目录]")
        print()
        print("示例:")
        print("  python download_draft.py list")
        print("  python download_draft.py download isgHa8JLYqIyiWuvAHOebhDv6xe150xKPFrcRc1pUi1YpLTCCf9ffoKNSzjT8-8O")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        list_drafts(count)

    elif command == "download":
        if len(sys.argv) < 3:
            print("❌ 请提供草稿的 media_id")
            print("   使用 'python download_draft.py list' 查看所有草稿")
            sys.exit(1)

        media_id = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "output/drafts"

        download_draft(media_id, output_dir)

    else:
        print(f"❌ 未知命令: {command}")
        print("   可用命令: list, download")
        sys.exit(1)
