"""Security utilities: JWT encoding/decoding and password hashing."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时
REFRESH_TOKEN_EXPIRE_DAYS = 30


class TokenError(Exception):
    """Token相关错误。"""
    pass


@dataclass
class TokenPayload:
    """Token解析后的数据。"""
    user_id: str
    token_type: str  # "access" or "refresh"
    exp: int


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> dict[str, Any]:
    """创建访问Token，返回包含access_token和过期时间的字典。"""
    expire = datetime.now(
        timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    exp_timestamp = int(expire.timestamp())
    payload = {"user_id": user_id, "exp": exp_timestamp, "type": "access"}
    token = jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "access_token_expiration": exp_timestamp}


def create_refresh_token(user_id: str, expires_delta: timedelta | None = None) -> dict[str, Any]:
    """创建刷新Token，返回包含refresh_token和过期时间的字典。"""
    expire = datetime.now(
        timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    exp_timestamp = int(expire.timestamp())
    payload = {"user_id": user_id, "exp": exp_timestamp, "type": "refresh"}
    token = jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)
    return {"refresh_token": token, "refresh_token_expiration": exp_timestamp}


def create_token_pair(user_id: str) -> dict[str, Any]:
    """创建access_token和refresh_token对。"""
    return {**create_access_token(user_id), **create_refresh_token(user_id)}


def decode_token(token: str) -> TokenPayload:
    """解码并验证Token，返回TokenPayload对象。"""
    try:
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise TokenError("Token中缺少用户信息")
        return TokenPayload(user_id=str(user_id), token_type=payload.get("type", "access"), exp=payload.get("exp", 0))
    except jwt.ExpiredSignatureError:
        raise TokenError("Token已过期")
    except jwt.InvalidTokenError as e:
        raise TokenError(f"Token无效: {e}")


def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    """使用refresh_token刷新access_token。"""
    payload = decode_token(refresh_token)
    if payload.token_type != "refresh":
        raise TokenError("Token类型错误，需要refresh token")
    return create_access_token(payload.user_id)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码。"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """哈希密码。"""
    return pwd_context.hash(password)
