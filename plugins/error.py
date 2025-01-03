import asyncio
import logging
from typing import TYPE_CHECKING

from hydrogram import Client
from hydrogram.errors import FloodWait
from hydrogram.raw.types import UpdateBotStopped

from fstg.db_funcs import del_user
from fstg.utils import config

if TYPE_CHECKING:
    from hydrogram.raw.base import Update
    from hydrogram.types import Chat, User

    from fstg.base import Bot

logger = logging.getLogger(__name__)


@Client.on_error(errors=(Exception, FloodWait))
async def error_handlers(_: "Bot", __: "Update", error: "Exception") -> None:
    if isinstance(error, FloodWait):
        await asyncio.sleep(error.value)
    else:
        if config.DEBUG_MODE:
            if hasattr(error, "MESSAGE"):
                logger.error(error.MESSAGE, exc_info=False)
            else:
                logger.error(str(error), exc_info=False)
        else:
            return None


@Client.on_raw_update(group=1)
async def update_handler(_: "Bot", event: "Update", __: "User", ___: "Chat") -> None:
    if isinstance(event, UpdateBotStopped):
        if event.stopped:
            await del_user(event.user_id)
