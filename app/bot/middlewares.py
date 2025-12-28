"""Bot middlewares for logging, throttling, etc."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import TelegramObject, Update

from app.core.logger import logger


class LoggingMiddleware(BaseMiddleware):
    """记录所有更新的中间件。"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            user = None
            if event.message and event.message.from_user:
                user = event.message.from_user
            elif event.callback_query and event.callback_query.from_user:
                user = event.callback_query.from_user

            if user:
                logger.debug(f"Update from user {user.id} (@{user.username})")

        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):
    """简单的限流中间件，防止用户刷屏。"""

    def __init__(self, rate_limit: float = 0.5) -> None:
        self.rate_limit = rate_limit
        self._user_last_time: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        import time

        user_id = None
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user_id = event.message.from_user.id
            elif event.callback_query and event.callback_query.from_user:
                user_id = event.callback_query.from_user.id

        if user_id:
            now = time.time()
            last_time = self._user_last_time.get(user_id, 0)
            if now - last_time < self.rate_limit:
                logger.debug(f"Throttled user {user_id}")
                return None
            self._user_last_time[user_id] = now

        return await handler(event, data)


def setup_middlewares(dp: Dispatcher) -> None:
    """配置所有中间件。"""
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(ThrottlingMiddleware(rate_limit=0.5))
