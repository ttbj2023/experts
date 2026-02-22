"""
直接上传 HTML 到微信公众号草稿箱
"""
import sys
import re
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.wechat.api_client import WeChatApiClient
from src.utils.logger import setup_logging, get_logger
from bs4 import BeautifulSoup

# 初始化日志
setup_logging()
logger = get_logger(__name__)


def upload_html_to_draft(html_file: str, use_cover: bool = True):
    """
    上传 HTML 文件到微信公众号草稿箱

    Args:
        html_file: HTML 文件路径
        use_cover: 是否使用封面图（默认 True）
    """
    # 读取 HTML 文件
    html_path = Path(html_file)
    if not html_path.exists():
        print(f"❌ 文件不存在: {html_file}")
        return

    html_content = html_path.read_text(encoding="utf-8")

    # 提取标题和作者
    soup = BeautifulSoup(html_content, "lxml")

    # 提取主标题（第一个 h1）
    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.get_text().strip()
    else:
        # 使用文件名作为标题
        title = html_path.stem

    # 提取作者信息
    author = "Claude AI"
    author_pattern = re.compile(r'作者\s*[:|]\s*([^\n<]+)')
    author_match = author_pattern.search(html_content)
    if author_match:
        author = author_match.group(1).strip()

    # 生成摘要（从第一段文字提取）
    summary = "本文探讨人工智能发展的关键问题，分析AGI的未来路径。"
    summary_pattern = re.compile(r'<p[^>]*>.*?本文.*?</p>', re.DOTALL)
    summary_match = summary_pattern.search(html_content)
    if summary_match:
        from html import unescape
        summary_text = summary_match.group(0)
        summary_text = re.sub(r'<[^>]+>', '', summary_text)  # 移除标签
        summary = unescape(summary_text).strip()
        if len(summary) > 100:
            summary = summary[:97] + "..."

    print(f"📝 标题: {title}")
    print(f"✍️  作者: {author}")
    print(f"📄 摘要: {summary}")

    # 初始化微信 API 客户端
    wechat_client = WeChatApiClient()

    # 上传封面图
    thumb_media_id = ""
    if use_cover:
        print("📷 上传封面图...")
        try:
            # 创建简单的封面图
            from scripts.create_simple_cover import create_cover_image
            cover_path = create_cover_image(
                text="AGI",
                output_path="output/temp_cover.png"
            )

            # 上传封面图到微信
            cover_result = wechat_client.upload_media(cover_path, "thumb")
            if cover_result and "media_id" in cover_result:
                thumb_media_id = cover_result["media_id"]
                print(f"✅ 封面图上传成功，media_id: {thumb_media_id}")
            else:
                print("⚠️  封面图上传失败，使用无封面模式")
        except Exception as e:
            print(f"⚠️  封面图处理失败: {e}，使用无封面模式")
    else:
        print("ℹ️  使用无封面模式")

    # 准备文章数据
    article_data = {
        "title": title,
        "author": author,
        "digest": summary,
        "content": html_content,
        "thumb_media_id": thumb_media_id,
        "show_cover_pic": 0,  # 不显示封面图
        "content_source_url": "",  # 原文链接
    }

    # 上传到草稿箱
    print("📤 正在上传到草稿箱...")
    media_id = wechat_client.upload_news_draft([article_data])

    if media_id:
        print(f"✅ 上传成功！")
        print(f"📋 草稿 media_id: {media_id}")
        print(f"\n🔗 请在微信公众号后台查看草稿箱")
    else:
        print("❌ 上传失败")
        print("💡 请检查 .env 配置文件中的微信配置")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/upload_to_draft.py <html_file>")
        print("选项:")
        print("  --no-cover    不使用封面图")
        sys.exit(1)

    html_file = sys.argv[1]
    use_cover = "--no-cover" not in sys.argv

    upload_html_to_draft(html_file, use_cover)
