import asyncio
import logging

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from hydrogram import Client
from hydrogram.enums import ParseMode
from hydrogram.types import BotCommand, BotCommandScopeAllPrivateChats

from fstg.utils import config

from .db_client import database

logger = logging.getLogger(__name__)


class Bot(Client):
    def __init__(self) -> None:
        super().__init__(
            name=config.BOT_ID,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            workers=4,
            plugins={"root": "plugins"},
            sleep_threshold=900,
        )

    async def start(self) -> None:
        await database.connect()

        try:
            await super().start()
        except Exception as exception:
            if hasattr(exception, "MESSAGE"):
                logger.error(exception.MESSAGE, exc_info=False)
            else:
                logger.error(str(exception), exc_info=False)
        else:
            await self.bot_commands_setup()
            self.set_parse_mode(ParseMode.HTML)

    async def stop(self) -> None:
        await database.close()

        if self.is_connected:
            await super().stop()

    async def bot_commands_setup(self) -> None:
        await self.delete_bot_commands()

        await self.set_bot_commands(
            commands=[
                BotCommand("start", "Start Bot"),
                BotCommand("ping", "Server Latency"),
                BotCommand("uptime", "Bot Uptime"),
                BotCommand("privacy", "Privacy Policy"),
            ],
            scope=BotCommandScopeAllPrivateChats(),
        )


Bot: "Bot" = Bot()
