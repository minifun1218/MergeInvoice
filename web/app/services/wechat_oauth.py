"""
微信OAuth服务
"""
from typing import Optional
from urllib.parse import urlencode

from app.config import settings


class WechatOAuthService:
    """微信OAuth服务"""

    @staticmethod
    def get_auth_url(state: str) -> str:
        """获取微信授权URL"""
        params = {
            "appid": settings.wechat_app_id,
            "redirect_uri": settings.wechat_redirect_uri,
            "response_type": "code",
            "scope": "snsapi_login",
            "state": state,
        }
        return f"https://open.weixin.qq.com/connect/qrconnect?{urlencode(params)}#wechat_redirect"

    @staticmethod
    async def get_access_token(code: str) -> Optional[dict]:
        """通过code获取access_token"""
        import aiohttp

        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            "appid": settings.wechat_app_id,
            "secret": settings.wechat_app_secret,
            "code": code,
            "grant_type": "authorization_code",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    if "errcode" in data:
                        return None
                    return data
        except Exception:
            return None

    @staticmethod
    async def get_user_info(access_token: str, openid: str) -> Optional[dict]:
        """获取微信用户信息"""
        import aiohttp

        url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            "access_token": access_token,
            "openid": openid,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    if "errcode" in data:
                        return None
                    return data
        except Exception:
            return None
