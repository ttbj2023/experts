"""
创建一个简单的封面图
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_cover_image(
    text: str = "AGI",
    output_path: str = "output/cover_simple.png",
    color: tuple = (0, 64, 128)  # Demis Hassabis 风格的深蓝色
):
    """
    创建一个简单的封面图

    Args:
        text: 封面文字
        output_path: 输出路径
        color: 背景颜色 (R, G, B)
    """
    # 创建图片
    width, height = 900, 500  # 微信推荐的封面图尺寸
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体
    try:
        # Linux 常见字体路径
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
        ]

        font = None
        for font_path in font_paths:
            if Path(font_path).exists():
                font = ImageFont.truetype(font_path, 120)
                break

        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # 获取文字大小
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 计算居中位置
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # 绘制文字（白色）
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # 保存图片
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)

    print(f"✅ 封面图已创建: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    create_cover_image()
