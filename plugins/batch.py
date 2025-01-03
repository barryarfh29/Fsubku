from typing import TYPE_CHECKING, Optional

from hydrogram import Client, filters
from hydrogram.errors import ListenerStopped, ListenerTimeout
from hydrogram.helpers import ikb

from fstg.filters import filter_authorized
from fstg.helpers import button
from fstg.utils import config, url_safe

if TYPE_CHECKING:
    from hydrogram.types import Message

    from fstg.base import Bot


@Client.on_message(filter_authorized & filters.command("batch"))
async def batch_handler(client: "Bot", message: "Message") -> None:
    first_message_id = await listen_for_message_id(client, message, "Start Message")
    if not first_message_id:
        return

    last_message_id = await listen_for_message_id(client, message, "Finish Message")
    if not last_message_id:
        return

    db_chat_id = config.DATABASE_CHAT_ID
    encoded_data = url_safe.encode_data(
        f"id-{first_message_id * abs(db_chat_id)}-{last_message_id * abs(db_chat_id)}"
    )
    encoded_data_url = f"https://t.me/{client.me.username}?start={encoded_data}"
    share_encoded_data_url = f"https://t.me/share?url={encoded_data_url}"

    await message.reply_text(
        f"<blockquote><b>{encoded_data_url}</b></blockquote>",
        quote=True,
        reply_markup=ikb([[("Share", share_encoded_data_url, "url")]]),
        disable_web_page_preview=True,
    )


async def listen_for_message_id(
    client: "Bot", message: "Message", prompt_message: str
) -> Optional[int]:
    chat_id, user_id = message.chat.id, message.from_user.id

    listen_message = await message.reply_text(
        f"<pre language='{prompt_message}'>Forward Message from Database Channel!</pre>\n"
        "<pre language=Timeout>45 Seconds</pre>",
        reply_markup=ikb(button.Cancel),
    )

    try:
        listening = await client.listen(chat_id=chat_id, user_id=user_id, timeout=45)
    except ListenerStopped:
        await listen_message.edit_text(
            "<blockquote><b>Process Cancelled!</b></blockquote>"
        )
        return None
    except ListenerTimeout:
        await listen_message.edit_text("<pre language=Timeout>Process Cancelled!</pre>")
        return None

    if not (
        listening.forward_from_chat
        and listening.forward_from_chat.id == config.DATABASE_CHAT_ID
    ):
        await listening.reply_text(
            "<pre language='Message Invalid'>Forward Message from Database Channel!</pre>",
            quote=True,
        )
        await listen_message.delete()
        return None

    await listen_message.delete()
    return listening.forward_from_message_id
