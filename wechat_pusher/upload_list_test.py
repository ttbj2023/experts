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

def upload_test_html():
    """上传测试HTML"""
    html_path = Path("output/test_list_formats.html")
    html_content = html_path.read_text(encoding='utf-8')

    # 生成摘要
    import re
    text_content = re.sub(r'<[^>]+>', '', html_content)[:120]

    # 创建封面
    cover_path = html_path.parent / "test_list_formats_cover.png"
    create_cover(str(cover_path), "列表格式测试")

    print(f"📝 上传测试文章: 列表格式测试")

    client = WeChatApiClient()

    # 上传封面
    print("📤 上传封面图...")
    cover_result = client.upload_media(str(cover_path), "image")
    if not cover_result:
        print("❌ 封面上传失败")
        return False

    # 准备文章
    article = {
        "title": "列表格式测试 - 9种格式对比",
        "author": "饕韬不绝",
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
        print(f"\n📋 请在微信公众号后台查看以下测试：")
        print(f"   1. li内直接文本")
        print(f"   2. li内使用p标签")
        print(f"   3. li内使用span标签")
        print(f"   4. 无冒号")
        print(f"   5. 冒号后空格")
        print(f"   6. 冒号后无空格")
        print(f"   7. 长文本直接文本")
        print(f"   8. 长文本使用span包裹")
        print(f"   9. 使用section包裹li内容")
        print(f"\n💡 查看哪种格式在'1.'或'•'后面没有换行符")
        return True
    return False

if __name__ == "__main__":
    upload_test_html()
