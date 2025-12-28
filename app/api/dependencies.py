"""FastAPI dependencies for authentication and authorization."""

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.utils.security import TokenError, decode_token


class JWTBearer(HTTPBearer):
    """JWT Bearer认证，用于路由依赖注入。"""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证凭证")
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证方式错误")
        try:
            payload = decode_token(credentials.credentials)
            if payload.token_type != "access":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token类型错误")
            return {"token": credentials.credentials, "user_id": payload.user_id}
        except TokenError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


class OptionalJWTBearer(HTTPBearer):
    """可选的JWT Bearer认证，未登录返回None。"""

    def __init__(self):
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> dict | None:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or credentials.scheme != "Bearer":
            return None
        try:
            payload = decode_token(credentials.credentials)
            if payload.token_type != "access":
                return None
            return {"token": credentials.credentials, "user_id": payload.user_id}
        except TokenError:
            return None


# 依赖实例
jwt_bearer = JWTBearer()
optional_jwt_bearer = OptionalJWTBearer()
