import asyncio
import datetime
from typing import TYPE_CHECKING

from hydrogram import Client, filters
from hydrogram.helpers import ikb

from fstg.db_funcs import get_users
from fstg.filters import filter_authorized
from fstg.helpers import button, cache
from fstg.utils import convert_seconds

if TYPE_CHECKING:
    from hydrogram.types import Message

    from fstg.base import Bot

startup_time = asyncio.get_running_loop().time()


@Client.on_message(filter_authorized & filters.command("users"))
async def users_handler(_: "Bot", message: "Message") -> None:
    counting_message = await message.reply_text(
        "<blockquote><b>Counting...</b></blockquote>", quote=True
    )

    all_users = await get_users()
    bot_users = [user for user in all_users if user not in cache.admins]
    len_users = len(all_users)

    await counting_message.edit_text(
        "<pre language='Bot Users'>"
        f"Admins : {len(cache.admins)}\nMembers: {len(bot_users)}</pre>\n"
        f"<pre language='Total'>{len_users} {'User' if len_users <= 1 else 'Users'}</pre>",
        reply_markup=ikb(button.Close),
    )


@Client.on_message(filters.private & filters.command("uptime"))
async def uptime_handler(client: "Bot", message: "Message") -> None:
    uptime_text = uptime_func(client)

    await message.reply_text(uptime_text, quote=True, reply_markup=ikb(button.Close))


def uptime_func(client: "Bot") -> str:
    total_seconds = client.loop.time() - startup_time
    converted_str = convert_seconds(total_seconds)

    startup_date = datetime.datetime.now() - datetime.timedelta(seconds=total_seconds)
    fmt_date_str = startup_date.strftime("%B %d, %Y at %I:%M %p")
    return (
        f"<pre language='Uptime Since'>{fmt_date_str}</pre>\n"
        f"<pre language='Uptime Total'>{converted_str}</pre>"
    )
