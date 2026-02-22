#!/usr/bin/env python3
"""
上传文章到微信公众号草稿箱（自动生成封面）
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.wechat.api_client import WeChatApiClient
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# 加载环境变量
load_dotenv()

def create_default_cover(output_path: str, title: str = "文章"):
    """创建默认封面图"""
    # 创建一个800x600的图片，深蓝色背景
    img = Image.new('RGB', (800, 600), color='#004080')
    draw = ImageDraw.Draw(img)
    
    # 添加标题文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
    except:
        # 如果找不到，使用默认字体
        font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (800 - text_width) / 2
    y = (600 - text_height) / 2
    
    # 绘制文字
    draw.text((x, y), title, fill='white', font=font)
    
    # 保存
    img.save(output_path)
    print(f"✅ 默认封面已创建: {output_path}")
    return output_path

def upload_html_to_draft(html_file: str, title: str = None, author: str = "原创"):
    """
    上传HTML文章到微信公众号草稿箱
    """
    # 读取HTML内容
    html_path = Path(html_file)
    if not html_path.exists():
        print(f"❌ 文件不存在: {html_file}")
        return False
    
    html_content = html_path.read_text(encoding='utf-8')
    
    # 如果没有提供标题，使用文件名
    if not title:
        title = html_path.stem
    
    # 生成摘要
    import re
    text_content = re.sub(r'<[^>]+>', '', html_content)
    text_content = text_content.strip()
    digest = text_content[:120] if len(text_content) > 120 else text_content
    
    # 创建并上传封面图
    cover_path = html_path.parent / f"{html_path.stem}_cover.png"
    create_default_cover(str(cover_path), title)
    
    print(f"\n📝 准备上传文章:")
    print(f"   标题: {title}")
    print(f"   作者: {author}")
    print()
    
    try:
        client = WeChatApiClient()
        
        # 上传封面图
        print("📤 上传封面图...")
        cover_result = client.upload_media(str(cover_path), "image")
        
        if not cover_result or not cover_result.get("media_id"):
            print("❌ 封面图上传失败")
            return False
        
        cover_media_id = cover_result["media_id"]
        print(f"✅ 封面图上传成功 (media_id: {cover_media_id})")
        
        # 准备文章数据
        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": html_content,
            "thumb_media_id": cover_media_id,
            "show_cover_pic": 1,
            "content_source_url": "",
        }
        
        # 上传草稿
        print("📤 上传草稿箱...")
        media_id = client.upload_news_draft([article])
        
        if media_id:
            print(f"\n✅ 上传成功!")
            print(f"   草稿media_id: {media_id}")
            print(f"   请在微信公众号后台 → 草稿箱查看")
            return True
        else:
            print(f"❌ 上传失败")
            return False
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python upload_to_draft.py <html文件> [标题] [作者]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    author = sys.argv[3] if len(sys.argv) > 3 else "原创"
    
    upload_html_to_draft(html_file, title, author)
