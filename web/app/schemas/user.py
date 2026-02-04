"""
用户相关Schema
"""
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础字段"""
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str
    confirm_password: str = Field(alias="confirmPassword")

    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: str = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: UserResponse


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求"""
    code: str
    state: str


class OAuthUrlResponse(BaseModel):
    """OAuth授权URL响应"""
    url: str
