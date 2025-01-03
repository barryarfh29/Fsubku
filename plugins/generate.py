from typing import TYPE_CHECKING, List

from hydrogram import Client, filters
from hydrogram.helpers import ikb

from fstg.filters import filter_generate
from fstg.utils import config, url_safe

if TYPE_CHECKING:
    from hydrogram.types import Message

    from fstg.base import Bot

commands: List[str] = [
    "batch",
    "bcast",
    "ping",
    "privacy",
    "start",
    "users",
    "uptime",
    "e",
    "sh",
]


@Client.on_message(filter_generate & (~filters.command(commands) & ~filters.service))
async def generate_handler(client: "Bot", message: "Message") -> None:
    database_chat_id = config.DATABASE_CHAT_ID
    database_message = await message.copy(database_chat_id)

    encoded_data = url_safe.encode_data(
        f"id-{database_message.id * abs(database_chat_id)}"
    )
    encoded_data_url = f"https://t.me/{client.me.username}?start={encoded_data}"

    share_encoded_data_url = f"https://t.me/share/url?url={encoded_data_url}"

    await message.reply_text(
        f"<blockquote><b>{encoded_data_url}</b></blockquote>",
        quote=True,
        reply_markup=ikb([[("Share", share_encoded_data_url, "url")]]),
        disable_web_page_preview=True,
    )
