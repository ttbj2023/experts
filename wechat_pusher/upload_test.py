#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.wechat.api_client import WeChatApiClient
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

def create_cover(output_path: str, title: str):
    """创建封面"""
    img = Image.new('RGB', (800, 600), color='#004080')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 50)
    except:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    x = (800 - text_width) / 2
    y = (600 - (text_bbox[3] - text_bbox[1])) / 2
    draw.text((x, y), title, fill='white', font=font)
    img.save(output_path)

def upload_to_draft(html_file: str, title: str, author: str):
    """上传到草稿箱"""
    html_path = Path(html_file)
    html_content = html_path.read_text(encoding='utf-8')
    
    # 生成摘要
    import re
    text_content = re.sub(r'<[^>]+>', '', html_content)[:120]
    
    # 创建封面
    cover_path = html_path.parent / f"{html_path.stem}_cover.png"
    create_cover(str(cover_path), title)
    
    print(f"📝 上传测试文章: {title}")
    
    client = WeChatApiClient()
    
    # 上传封面
    print("📤 上传封面图...")
    cover_result = client.upload_media(str(cover_path), "image")
    if not cover_result:
        print("❌ 封面上传失败")
        return False
    
    # 准备文章
    article = {
        "title": title,
        "author": author,
        "digest": text_content,
        "content": html_content,
        "thumb_media_id": cover_result["media_id"],
        "show_cover_pic": 1,
        "content_source_url": "",
    }
    
    # 上传草稿
    print("📤 上传草稿箱...")
    media_id = client.upload_news_draft([article])
    
    if media_id:
        print(f"✅ 上传成功!")
        print(f"   草稿media_id: {media_id}")
        return True
    return False

if __name__ == "__main__":
    upload_to_draft(
        "output/content_inflation_article/article.html",
        "当AI连「影视飓风Tim」都能完美复制：我们正滑向「信息恶性通胀」的深渊",
        "饕韬不绝"
    )
