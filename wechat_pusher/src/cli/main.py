"""
WeChat Pusher - 微信公众号AI自动化推送系统
命令行工具（简化版）
"""
import sys
from pathlib import Path
import click

from src.utils.logger import setup_logging, get_logger
from src.converter.markdown_parser import MarkdownParser
from src.workflow.publisher import article_publisher

# 初始化日志
setup_logging()
logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """WeChat Pusher - 微信公众号AI自动化推送系统"""
    pass


@cli.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Path(), help="输出HTML文件路径", default=None
)
@click.option(
    "--summary", "-s", type=str, help="文章摘要（可选）", default=None
)
def convert(markdown_file: str, output: str, summary: str):
    """
    将Markdown文件转换为微信公众号格式HTML

    示例:
        wechat-pusher convert article.md
        wechat-pusher convert article.md -o output.html
        wechat-pusher convert article.md -s "这是摘要"
    """
    try:
        logger.info(f"开始转换文件: {markdown_file}")

        # 读取内容
        content = Path(markdown_file).read_text(encoding="utf-8")

        # 使用新转换器
        parser = MarkdownParser()
        html = parser.parse_content(content=content, summary=summary)

        # 保存HTML
        if not output:
            output = str(Path(markdown_file).with_suffix(".html"))

        Path(output).write_text(html, encoding="utf-8")

        logger.info(f"✅ 转换成功！HTML已保存到: {output}")
        click.echo(f"✅ 转换成功！\n📄 HTML已保存到: {output}")

    except Exception as e:
        logger.error(f"转换失败: {e}")
        click.echo(f"❌ 转换失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option(
    "--author", "-a", type=str, help="作者名称（不指定则使用配置文件中的默认值）", default=None
)
def publish(markdown_file: str, author: str):
    """
    自动发布文章到微信公众号草稿箱（完整AI增强流程）

    流程：
        1. 解析Markdown文件
        2. AI分析（生成摘要、配图提示词、图表分析）
        3. 生成封面图、插图、图表
        4. 上传素材到微信
        5. 转换为微信HTML（嵌入图片）
        6. 创建草稿

    示例:
        wechat-pusher publish article.md
        wechat-pusher publish article.md --author "张三"
    """
    try:
        click.echo("=" * 80)
        click.echo("🚀 开始自动发布流程")
        click.echo("=" * 80)
        click.echo()

        # 设置作者
        if author:
            article_publisher.fixed_author = author
            click.echo(f"👤 作者: {author}")
        else:
            click.echo(f"👤 作者: {article_publisher.fixed_author}")

        click.echo()

        # 执行发布
        success = article_publisher.publish(markdown_file)

        if success:
            click.echo()
            click.echo("=" * 80)
            click.echo("🎉 发布成功！")
            click.echo("=" * 80)
            click.echo()
            click.echo("💡 下一步:")
            click.echo("   1. 登录微信公众平台: https://mp.weixin.qq.com")
            click.echo("   2. 进入草稿箱")
            click.echo("   3. 编辑并发布文章")
            click.echo()
        else:
            click.echo()
            click.echo("=" * 80)
            click.echo("❌ 发布失败")
            click.echo("=" * 80)
            click.echo()
            click.echo("💡 提示:")
            click.echo("   - 检查日志文件了解详细错误信息")
            click.echo("   - 确认微信API配置正确（AppID和Secret）")
            click.echo("   - 确认网络连接正常")
            click.echo()
            sys.exit(1)

    except Exception as e:
        logger.error(f"发布失败: {e}")
        click.echo(f"\n❌ 发布失败: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli()
