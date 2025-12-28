"""Bot Manager for managing multiple Telegram bots."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.core.logger import logger


class BotMode(Enum):
    """Bot运行模式。"""

    POLLING = "polling"
    WEBHOOK = "webhook"


@dataclass
class BotInstance:
    """单个Bot实例的封装。"""

    name: str
    token: str
    mode: BotMode = BotMode.POLLING
    webhook_path: str = ""
    webhook_base_url: str = ""
    bot: Bot = field(init=False)
    dp: Dispatcher = field(init=False)
    _polling_task: asyncio.Task | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.bot = Bot(
            token=self.token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
        )
        self.dp = Dispatcher()
        if not self.webhook_path:
            self.webhook_path = f"/webhook/{self.name}"

    @property
    def is_polling(self) -> bool:
        """是否使用polling模式。"""
        return self.mode == BotMode.POLLING

    async def start(self) -> None:
        """启动Bot。"""
        if self.is_polling:
            await self._start_polling()
        else:
            await self._setup_webhook()

    async def _start_polling(self) -> None:
        """启动polling模式。"""
        await self.bot.delete_webhook(drop_pending_updates=True)
        logger.info(f"Bot '{self.name}' starting polling")
        self._polling_task = asyncio.create_task(
            self.dp.start_polling(self.bot, handle_signals=False)
        )

    async def _setup_webhook(self) -> None:
        """设置webhook模式。"""
        if not self.webhook_base_url:
            raise ValueError(
                f"Bot '{self.name}': webhook_base_url is required for webhook mode")

        webhook_url = f"{self.webhook_base_url}{self.webhook_path}"
        await self.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        logger.info(f"Bot '{self.name}' webhook set to {webhook_url}")

    async def stop(self) -> None:
        """停止Bot。"""
        if self.is_polling and self._polling_task:
            await self.dp.stop_polling()
            self._polling_task.cancel()
            self._polling_task = None

        await self.bot.session.close()
        logger.info(f"Bot '{self.name}' stopped")

    async def feed_update(self, update_data: dict) -> None:
        """处理webhook更新（仅webhook模式使用）。"""
        from aiogram.types import Update

        update = Update.model_validate(update_data)
        await self.dp.feed_update(self.bot, update)


class BotManager:
    """
    Bot管理器，管理多个独立的Bot实例。

    每个Bot可以独立配置运行模式（polling/webhook）。

    使用方式:
        manager = BotManager()
        manager.register("main", token, use_polling=True)
        manager.register("notify", token2, use_polling=False, webhook_base_url="https://example.com")
        await manager.start()
        await manager.stop()
    """

    def __init__(self) -> None:
        self._bots: dict[str, BotInstance] = {}

    def register(
        self,
        name: str,
        token: str,
        setup_func: "Callable[[Dispatcher], None] | None" = None,
        use_polling: bool = True,
        webhook_path: str = "",
        webhook_base_url: str = "",
    ) -> BotInstance:
        """
        注册一个Bot。

        Args:
            name: Bot名称，用于标识
            token: Telegram Bot Token
            setup_func: 配置函数，用于注册handlers和middlewares
            use_polling: True使用polling，False使用webhook
            webhook_path: 自定义webhook路径，默认为 /webhook/{name}
            webhook_base_url: Webhook基础URL，webhook模式必填

        Returns:
            BotInstance实例
        """
        if name in self._bots:
            logger.warning(
                f"Bot '{name}' already registered, will be replaced")

        mode = BotMode.POLLING if use_polling else BotMode.WEBHOOK
        instance = BotInstance(
            name=name,
            token=token,
            mode=mode,
            webhook_path=webhook_path,
            webhook_base_url=webhook_base_url,
        )

        if setup_func:
            setup_func(instance.dp)

        self._bots[name] = instance
        logger.info(f"Bot '{name}' registered (mode={mode.value})")
        return instance

    def get(self, name: str) -> BotInstance | None:
        """获取指定名称的Bot实例。"""
        return self._bots.get(name)

    def get_bot(self, name: str) -> Bot | None:
        """获取指定名称的Bot对象。"""
        instance = self._bots.get(name)
        return instance.bot if instance else None

    async def start(self) -> None:
        """启动所有Bot。"""
        if not self._bots:
            logger.warning("No bots registered")
            return

        for instance in self._bots.values():
            await instance.start()

    async def stop(self) -> None:
        """停止所有Bot。"""
        if not self._bots:
            return

        logger.info("Stopping all bots")
        for instance in self._bots.values():
            await instance.stop()

        self._bots.clear()


# 全局Bot管理器实例
bot_manager = BotManager()


def setup_default_bot(dp: Dispatcher) -> None:
    """配置默认Bot的handlers和middlewares。"""
    from app.bot.handlers import register_handlers
    from app.bot.middlewares import setup_middlewares

    setup_middlewares(dp)
    register_handlers(dp)


def init_bot_manager() -> BotManager:
    """
    初始化并配置Bot管理器。

    Returns:
        配置好的BotManager实例
    """
    # 从配置注册所有Bot
    for bot_config in settings.bots:
        use_polling = bot_config.mode == "polling" or bot_config.mode == "dev"
        bot_manager.register(
            name=bot_config.name,
            token=bot_config.token,
            setup_func=setup_default_bot,
            use_polling=use_polling,
            webhook_base_url=bot_config.webhook_url.rsplit(
                "/", 1)[0] if bot_config.webhook_url else "",
        )

    return bot_manager
