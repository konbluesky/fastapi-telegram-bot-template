"""Keyboard builders for common UI patterns."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)


def webapp_keyboard(url: str, text: str = "🎴 打开游戏") -> InlineKeyboardMarkup:
    """创建WebApp启动按钮。"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))]
        ]
    )


def confirm_keyboard(
    confirm_text: str = "✅ 确认",
    cancel_text: str = "❌ 取消",
    confirm_data: str = "confirm",
    cancel_data: str = "cancel",
) -> InlineKeyboardMarkup:
    """创建确认/取消键盘。"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=confirm_text, callback_data=confirm_data),
                InlineKeyboardButton(
                    text=cancel_text, callback_data=cancel_data),
            ]
        ]
    )


def pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str = "page",
) -> InlineKeyboardMarkup:
    """创建分页键盘。"""
    buttons = []

    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="◀️", callback_data=f"{callback_prefix}:{current_page - 1}")
        )

    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}", callback_data="noop")
    )

    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text="▶️", callback_data=f"{callback_prefix}:{current_page + 1}")
        )

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """创建主菜单Reply键盘。"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎴 抽卡"), KeyboardButton(text="🎒 背包")],
            [KeyboardButton(text="🎰 PVP转盘"), KeyboardButton(text="📊 排行榜")],
            [KeyboardButton(text="👤 我的"), KeyboardButton(text="❓ 帮助")],
        ],
        resize_keyboard=True,
    )
