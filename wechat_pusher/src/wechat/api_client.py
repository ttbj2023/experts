"""
微信公众号API客户端
用于上传素材和创建草稿
"""
import os
import json
import time
from typing import Optional, Dict, List
from pathlib import Path
import requests

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WeChatApiClient:
    """微信公众号API客户端"""

    def __init__(self):
        """初始化客户端"""
        self.appid = config.wechat.appid
        self.secret = config.wechat.secret
        self.access_token = None
        self.token_expires_at = 0

        logger.info(f"WeChat API客户端初始化完成 (AppID: {self.appid})")

    def _get_access_token(self) -> str:
        """
        获取access_token

        Returns:
            str: access_token
        """
        # 检查token是否过期
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        # 获取新的access_token
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret
        }

        try:
            logger.info("获取微信access_token...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "access_token" in data:
                self.access_token = data["access_token"]
                # 提前5分钟过期
                self.token_expires_at = time.time() + data["expires_in"] - 300
                logger.info(f"access_token获取成功，过期时间: {data['expires_in']}秒")
                return self.access_token
            else:
                error_msg = data.get("errmsg", "未知错误")
                error_code = data.get("errcode", "未知")
                raise Exception(f"获取access_token失败: {error_code} - {error_msg}")

        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            raise

    def upload_media(self, file_path: str, media_type: str = "image") -> Optional[Dict]:
        """
        上传永久素材

        Args:
            file_path: 文件路径
            media_type: 素材类型（image/thumb/video）

        Returns:
            dict: 素材信息，失败返回None
            {
                "media_id": "xxx",
                "url": "https://mmbiz.qpic.cn/..."
            }
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None

        try:
            # 获取access_token
            access_token = self._get_access_token()

            # 构建URL
            url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={media_type}"

            # 准备文件
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                files = {
                    'media': (file_name, f, 'image/png')
                }

                logger.info(f"上传素材: {file_name}")
                response = requests.post(url, files=files, timeout=60)
                response.raise_for_status()

                data = response.json()

                if "media_id" in data:
                    result = {
                        "media_id": data["media_id"],
                        "url": data.get("url", "")
                    }
                    logger.info(f"素材上传成功，media_id: {result['media_id']}, url: {result['url'][:80]}...")
                    return result
                else:
                    error_msg = data.get("errmsg", "未知错误")
                    error_code = data.get("errcode", "未知")
                    logger.error(f"上传素材失败: {error_code} - {error_msg}")
                    return None

        except Exception as e:
            logger.error(f"上传素材异常: {e}")
            return None

    def upload_news_draft(
        self,
        articles: List[Dict]
    ) -> Optional[str]:
        """
        上传草稿箱

        Args:
            articles: 文章列表
                [
                    {
                        "title": "标题",
                        "author": "作者",
                        "digest": "摘要",
                        "content": "HTML内容",
                        "thumb_media_id": "封面图media_id",
                        "show_cover_pic": 1,  # 是否显示封面图
                        "content_source_url": "",  # 原文链接
                        "thumb_url": ""  # 封面图URL（可选）
                    }
                ]

        Returns:
            str: 草稿media_id，失败返回None
        """
        try:
            # 获取access_token
            access_token = self._get_access_token()

            # 构建URL
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

            # 构建请求数据
            payload = {
                "articles": articles
            }

            # 调试：检查标题长度
            for i, article in enumerate(articles):
                title = article.get("title", "")
                title_utf8_bytes = len(title.encode('utf-8'))
                title_gbk_bytes = len(title.encode('gbk'))
                logger.info(f"文章{i+1}标题调试: '{title}' (字符:{len(title)}, UTF-8:{title_utf8_bytes}字节, GBK:{title_gbk_bytes}字节)")

            logger.info(f"上传草稿箱，文章数量: {len(articles)}")
            logger.debug(f"完整请求数据: {payload}")  # 添加完整payload日志

            # 手动序列化JSON，使用ensure_ascii=False避免中文被转义为Unicode序列
            # 这样微信API能正确计算中文字符数
            json_data = json.dumps(payload, ensure_ascii=False)

            response = requests.post(
                url,
                data=json_data.encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if "media_id" in data:
                draft_media_id = data["media_id"]
                logger.info(f"草稿创建成功，media_id: {draft_media_id}")
                return draft_media_id
            else:
                error_msg = data.get("errmsg", "未知错误")
                error_code = data.get("errcode", "未知")
                logger.error(f"创建草稿失败: {error_code} - {error_msg}")
                return None

        except Exception as e:
            logger.error(f"创建草稿异常: {e}")
            return None

    def get_draft_list(self, offset: int = 0, count: int = 20, no_content: int = 0) -> Optional[Dict]:
        """
        获取草稿箱列表

        Args:
            offset: 从0开始的偏移量
            count: 返回数量（20以内）
            no_content: 是否不返回content字段（1=不返回，0=返回）。不返回content可以加快速度

        Returns:
            dict: 草稿列表信息，失败返回None
            {
                "total_count": 总数,
                "item_count": 本次返回数量,
                "item_list": [
                    {
                        "media_id": "xxx",
                        "content": {
                            "news_item": [
                                {
                                    "title": "标题",
                                    "author": "作者",
                                    "digest": "摘要",
                                    "content": "HTML内容",
                                    "thumb_media_id": "封面图media_id",
                                    "show_cover_pic": 1,
                                    "url": "文章链接",
                                    "content_source_url": "原文链接"
                                }
                            ]
                        },
                        "update_time": 更新时间戳
                    }
                ]
            }
        """
        try:
            access_token = self._get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}"

            payload = {
                "offset": offset,
                "count": count,
                "no_content": no_content
            }

            logger.info(f"获取草稿列表: offset={offset}, count={count}, no_content={no_content}")

            # 使用POST请求
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "item" in data:
                result = {
                    "total_count": data.get("total_count", 0),
                    "item_count": len(data["item"]),
                    "item_list": data["item"]
                }
                logger.info(f"草稿列表获取成功: 共{result['total_count']}个，本次返回{result['item_count']}个")
                return result
            else:
                error_msg = data.get("errmsg", "未知错误")
                error_code = data.get("errcode", "未知")
                logger.error(f"获取草稿列表失败: {error_code} - {error_msg}")
                return None

        except Exception as e:
            logger.error(f"获取草稿列表异常: {e}")
            return None

    def get_material_list(self, material_type: str = "image", offset: int = 0, count: int = 20) -> Optional[Dict]:
        """
        获取永久素材列表

        Args:
            material_type: 素材类型（image/video/voice/thumb）
            offset: 从0开始的偏移量
            count: 返回数量（20以内）

        Returns:
            dict: 素材列表信息，失败返回None
            {
                "total_count": 总数,
                "item_count": 本次返回数量,
                "item_list": [
                    {
                        "media_id": "xxx",
                        "name": "文件名",
                        "url": "图片URL",
                        "update_time": 更新时间戳
                    }
                ]
            }
        """
        try:
            access_token = self._get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={access_token}"

            payload = {
                "type": material_type,
                "offset": offset,
                "count": count
            }

            logger.info(f"获取素材列表: type={material_type}, offset={offset}, count={count}")

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "item" in data:
                result = {
                    "total_count": data.get("total_count", 0),
                    "item_count": len(data["item"]),
                    "item_list": data["item"]
                }
                logger.info(f"素材列表获取成功: 共{result['total_count']}个，本次返回{result['item_count']}个")
                return result
            else:
                error_msg = data.get("errmsg", "未知错误")
                error_code = data.get("errcode", "未知")
                logger.error(f"获取素材列表失败: {error_code} - {error_msg}")
                return None

        except Exception as e:
            logger.error(f"获取素材列表异常: {e}")
            return None


# 创建全局实例
wechat_api_client = WeChatApiClient()
