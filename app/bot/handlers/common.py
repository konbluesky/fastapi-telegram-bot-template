"""Common bot handlers: /start, /help, webapp launch."""

import re

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.core.config import settings

router = Router(name="common")


def escape_md(text: str) -> str:
    """转义 MarkdownV2 特殊字符。"""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!\\])", r"\\\1", text)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """处理 /start 命令，显示欢迎信息和WebApp入口。"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎴 打开 {app_name}",
                    web_app=WebAppInfo(
                        url=f"{settings.bots.get_main_bot().app_url}"),
                )
            ],
            [InlineKeyboardButton(text="📖 帮助", callback_data="help")],
        ]
    )

    app_name = escape_md(settings.app_name)
    await message.answer(
        f"👋 使用 {app_name} 的 WebApp",
        reply_markup=keyboard,
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """处理 /help 命令。"""
    await message.answer(
        f"访问 https://github.com/Siykt/fastapi-telegram-bot-template 获取更多信息",
    )
