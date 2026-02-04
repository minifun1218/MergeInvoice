"""
用户数据模型
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean

from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(256), nullable=True, comment="密码哈希")
    nickname = Column(String(100), nullable=True, comment="昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    email = Column(String(100), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    is_active = Column(Boolean, default=True, comment="是否激活")

    # OAuth绑定
    wechat_openid = Column(String(100), nullable=True, unique=True, comment="微信OpenID")
    wechat_unionid = Column(String(100), nullable=True, comment="微信UnionID")

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
