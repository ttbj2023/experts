"""
测试微信API连接和配置
"""
import sys
sys.path.insert(0, '/mnt/wsl/PHYSICALDRIVE2/assistant-experts/wechat_pusher')

from src.wechat.api_client import wechat_api_client
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("=" * 80)
    print("🧪 测试微信API连接")
    print("=" * 80)
    print()

    # 显示出口IP信息
    print("🌐 服务器出口IP信息:")
    print(f"   真实出口IP: 117.88.1.211")
    print(f"   位置: 中国江苏南京")
    print(f"   运营商: 中国电信骨干网")
    print()
    print(f"💡 请在微信后台配置此IP: 117.88.1.211")
    print(f"   （不是代理IP 144.34.186.22）")
    print()

    # 显示配置信息
    print("📋 当前配置:")
    print(f"   AppID: {config.wechat.appid}")
    print(f"   Base URL: https://api.weixin.qq.com")
    print()

    # 检查AppID和Secret是否配置
    if config.wechat.appid == "wx1234567890abcdef":
        print("❌ 错误: 检测到默认AppID，请在.env中配置真实的微信AppID")
        print()
        print("💡 配置步骤:")
        print("   1. 编辑 .env 文件")
        print("   2. 设置 WECHAT_APPID=your_real_appid")
        print("   3. 设置 WECHAT_SECRET=your_real_secret")
        print()
        return

    if config.wechat.secret == "your-wechat-app-secret":
        print("❌ 错误: 检测到默认Secret，请在.env中配置真实的微信Secret")
        print()
        print("💡 获取Secret步骤:")
        print("   1. 登录 https://mp.weixin.qq.com")
        print("   2. 进入「开发」→「基本配置」")
        print("   3. 生成并复制「开发者密码（AppSecret）」")
        print()
        return

    print("✅ 配置检查通过")
    print()

    # 测试获取access_token
    print("=" * 80)
    print("🔑 测试获取access_token")
    print("=" * 80)
    print()

    try:
        print("⏳ 正在获取access_token...")
        access_token = wechat_api_client._get_access_token()

        if access_token:
            print(f"✅ access_token获取成功！")
            print(f"   Token长度: {len(access_token)}字符")
            print(f"   Token预览: {access_token[:20]}...")
            print()
            print("🎉 微信API连接测试成功！")
            print()
            print("💡 接下来可以:")
            print("   1. 运行完整发布流程: wechat-pusher publish article.md")
            print("   2. 测试素材上传功能")
            print("   3. 测试草稿创建功能")
        else:
            print("❌ access_token获取失败")
            print()
            print("💡 可能的原因:")
            print("   1. IP白名单未配置")
            print("      解决: 在微信公众平台添加IP 144.34.186.22")
            print("   2. AppID或Secret配置错误")
            print("      解决: 检查.env文件中的配置")
            print("   3. 网络连接问题")
            print("      解决: 检查是否能访问 api.weixin.qq.com")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print()
        print("💡 详细错误信息:")
        import traceback
        traceback.print_exc()

    print()


if __name__ == "__main__":
    main()
