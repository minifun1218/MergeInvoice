"""
用户认证服务
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserResponse
from app.utils.auth_utils import hash_password, verify_password, generate_token


class AuthService:
    """认证服务"""

    @staticmethod
    def generate_id() -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_wechat_openid(db: Session, openid: str) -> Optional[User]:
        """根据微信OpenID获取用户"""
        return db.query(User).filter(User.wechat_openid == openid).first()

    @staticmethod
    def register(
        db: Session,
        username: str,
        password: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> tuple[Optional[User], str]:
        """用户注册"""
        # 检查用户名是否存在
        if AuthService.get_by_username(db, username):
            return None, "用户名已存在"

        user_id = AuthService.generate_id()
        now = datetime.now()

        user = User(
            id=user_id,
            username=username,
            password_hash=hash_password(password),
            nickname=username,
            email=email,
            phone=phone,
            created_at=now,
            updated_at=now,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user, ""

    @staticmethod
    def login(db: Session, username: str, password: str) -> tuple[Optional[User], str]:
        """用户登录"""
        user = AuthService.get_by_username(db, username)

        if not user:
            return None, "用户不存在"

        if not user.password_hash:
            return None, "请使用第三方登录"

        if not verify_password(password, user.password_hash):
            return None, "密码错误"

        if not user.is_active:
            return None, "账户已被禁用"

        return user, ""

    @staticmethod
    def create_wechat_user(
        db: Session,
        openid: str,
        unionid: Optional[str],
        nickname: str,
        avatar: Optional[str],
    ) -> User:
        """创建微信用户"""
        user_id = AuthService.generate_id()
        now = datetime.now()

        user = User(
            id=user_id,
            username=f"wx_{openid[:8]}",
            nickname=nickname,
            avatar=avatar,
            wechat_openid=openid,
            wechat_unionid=unionid,
            created_at=now,
            updated_at=now,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def generate_login_token(user: User) -> str:
        """生成登录Token"""
        return generate_token(user.id)

    @staticmethod
    def to_response(user: User) -> UserResponse:
        """转换为响应对象"""
        return UserResponse(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            avatar=user.avatar,
            email=user.email,
            phone=user.phone,
            createdAt=user.created_at.isoformat() + "Z" if user.created_at else "",
        )
