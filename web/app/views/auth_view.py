"""
认证视图
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UserCreate, UserResponse, LoginRequest, LoginResponse,
    OAuthCallbackRequest, OAuthUrlResponse
)
from app.services.auth_service import AuthService
from app.services.wechat_oauth import WechatOAuthService
from app.utils.auth_utils import verify_token, generate_state

router = APIRouter(prefix="/auth")

# 存储OAuth state (生产环境应使用Redis)
oauth_states: dict[str, str] = {}


@router.post("/register", response_model=ApiResponse[LoginResponse])
async def register(request: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="两次密码不一致")

    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")

    user, error = AuthService.register(
        db,
        username=request.username,
        password=request.password,
        email=request.email,
        phone=request.phone,
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    token = AuthService.generate_login_token(user)

    return ApiResponse(
        code=0,
        message="注册成功",
        data=LoginResponse(
            token=token,
            user=AuthService.to_response(user),
        )
    )


@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user, error = AuthService.login(db, request.username, request.password)

    if error:
        raise HTTPException(status_code=400, detail=error)

    token = AuthService.generate_login_token(user)

    return ApiResponse(
        code=0,
        message="登录成功",
        data=LoginResponse(
            token=token,
            user=AuthService.to_response(user),
        )
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """获取当前用户信息"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    token = authorization[7:]
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Token无效或已过期")

    user = AuthService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return ApiResponse(
        code=0,
        message="success",
        data=AuthService.to_response(user),
    )


@router.post("/logout", response_model=ApiResponse[None])
async def logout(authorization: Optional[str] = Header(None)):
    """退出登录"""
    # Token无状态，客户端删除即可
    return ApiResponse(code=0, message="退出成功", data=None)


@router.get("/oauth/wechat/url", response_model=ApiResponse[OAuthUrlResponse])
async def get_wechat_oauth_url():
    """获取微信OAuth授权URL"""
    state = generate_state()
    oauth_states[state] = "wechat"

    url = WechatOAuthService.get_auth_url(state)

    return ApiResponse(
        code=0,
        message="success",
        data=OAuthUrlResponse(url=url),
    )


@router.post("/oauth/wechat/callback", response_model=ApiResponse[LoginResponse])
async def wechat_oauth_callback(
    request: OAuthCallbackRequest,
    db: Session = Depends(get_db),
):
    """微信OAuth回调"""
    # 验证state
    if request.state not in oauth_states:
        raise HTTPException(status_code=400, detail="无效的state")

    del oauth_states[request.state]

    # 获取access_token
    token_data = await WechatOAuthService.get_access_token(request.code)
    if not token_data:
        raise HTTPException(status_code=400, detail="获取access_token失败")

    openid = token_data.get("openid")
    access_token = token_data.get("access_token")
    unionid = token_data.get("unionid")

    # 获取用户信息
    user_info = await WechatOAuthService.get_user_info(access_token, openid)

    # 查找或创建用户
    user = AuthService.get_by_wechat_openid(db, openid)

    if not user:
        nickname = user_info.get("nickname", "微信用户") if user_info else "微信用户"
        avatar = user_info.get("headimgurl") if user_info else None
        user = AuthService.create_wechat_user(db, openid, unionid, nickname, avatar)

    token = AuthService.generate_login_token(user)

    return ApiResponse(
        code=0,
        message="登录成功",
        data=LoginResponse(
            token=token,
            user=AuthService.to_response(user),
        )
    )
