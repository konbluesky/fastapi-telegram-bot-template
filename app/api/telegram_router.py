"""Telegram Webhook 路由。"""

from fastapi import APIRouter, Path, Request
from fastapi.responses import Response

from app.bot import bot_manager

router = APIRouter(prefix="/tg-bot", tags=["telegram"])


@router.post(
    "/webhook/{bot_name}",
    summary="Telegram Webhook",
    description="接收 Telegram Bot 的 webhook 回调请求",
    responses={
        200: {"description": "处理成功"},
        404: {"description": "Bot不存在或未启用webhook模式"}
    },
)
async def webhook_handler(
        request: Request,
        bot_name: str = Path(..., description="Bot名称"),
) -> Response:
    """处理Telegram webhook请求。"""
    instance = bot_manager.get(bot_name)
    if not instance or instance.is_polling:
        return Response(status_code=404)

    await instance.feed_update(await request.json())
    return Response(status_code=200)
