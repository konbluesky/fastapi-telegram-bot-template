"""Bot command and message handlers."""

from aiogram import Dispatcher

from app.bot.handlers.common import router as common_router


def register_handlers(dp: Dispatcher) -> None:
    """注册所有handlers到dispatcher。"""
    dp.include_router(common_router)
