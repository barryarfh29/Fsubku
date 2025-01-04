import asyncio
import os
from typing import TYPE_CHECKING, List

import aiofiles
from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.utils import datetime_to_timestamp

from fstg.filters import filter_authorized, filter_generate
from fstg.utils import config, url_safe

if TYPE_CHECKING:
    from hydrogram.types import Message

    from fstg.base import Bot

commands: List[str] = [
    "batch",
    "bcast",
    "get",
    "ping",
    "privacy",
    "start",
    "users",
    "uptime",
    "e",
    "sh",
]

GENERATED_LINKS = []


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


@Client.on_message(filters.chat(config.DATABASE_CHAT_ID))
async def _generate_handler(client: "Bot", message: "Message") -> None:
    encoded_data = url_safe.encode_data(
        f"id-{message.id * abs(config.DATABASE_CHAT_ID)}"
    )
    encoded_data_url = f"https://t.me/{client.me.username}?start={encoded_data}"

    async with asyncio.Lock():
        GENERATED_LINKS.append(encoded_data_url)


@Client.on_message(filter_authorized & filters.command("get"))
async def get_handler(client: "Bot", message: "Message") -> None:
    if not GENERATED_LINKS:
        await message.reply_text(
            "<blockquote><b>No Links!</b></blockquote>", quote=True
        )
        return

    msg = await message.reply_text("blockquote><b>...</b></blockquote>")

    datetime_to_timestamp(message.date)
    path = f"{client.me.first_name}.txt"
    link = len(GENERATED_LINKS)

    async with asyncio.Lock():
        text = "\n".join(GENERATED_LINKS)

        async with aiofiles.open(path, mode="w") as file:
            await file.write(text)

        GENERATED_LINKS.clear()

    await message.reply_document(
        path,
        caption=(
            f"<code>Date :</code> {message.date}\n" f"<code>Total:</code> {link} Links"
        ),
    )
    await msg.delete()

    if os.path.isfile(path):
        os.remove(path)
