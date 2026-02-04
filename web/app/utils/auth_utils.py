"""
认证工具函数
"""
import hashlib
import uuid
import time
import hmac
from typing import Optional

from app.config import settings

# 从配置读取
SECRET_KEY = settings.secret_key
TOKEN_EXPIRE_HOURS = settings.token_expire_hours


def hash_password(password: str) -> str:
    """密码哈希"""
    salt = "invoice_salt_2024"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


def generate_token(user_id: str) -> str:
    """生成Token"""
    timestamp = int(time.time())
    expire = timestamp + TOKEN_EXPIRE_HOURS * 3600
    payload = f"{user_id}:{expire}"
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{payload}:{signature}"


def verify_token(token: str) -> Optional[str]:
    """验证Token，返回user_id"""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None

        user_id, expire_str, signature = parts
        expire = int(expire_str)

        # 检查过期
        if time.time() > expire:
            return None

        # 验证签名
        payload = f"{user_id}:{expire_str}"
        expected_sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]

        if signature != expected_sig:
            return None

        return user_id
    except Exception:
        return None


def generate_state() -> str:
    """生成OAuth state"""
    return str(uuid.uuid4())[:8]
