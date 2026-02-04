"""
应用配置 - 从 .env 文件加载
"""
import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings

# 加载 .env 文件
ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # 数据库配置
    database_url: str = "sqlite:///./invoice.db"

    # JWT配置
    secret_key: str = "invoice-merge-secret-key-2024"
    token_expire_hours: int = 168  # 7天

    # 微信开放平台配置
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    wechat_redirect_uri: str = "http://localhost:5173/oauth/wechat/callback"

    # MinIO 对象存储配置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "invoice"
    minio_secure: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
