from typing import TYPE_CHECKING, List
from os import environ

from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.errors import ListenerStopped, ListenerTimeout
from hydrogram.helpers import ikb

from fstg.db_funcs import (
    add_admin,
    add_fs_chat,
    del_admin,
    del_fs_chat,
    update_generate_status,
    update_protect_content,
    update_start_text_message,
)
from fstg.filters import filter_authorized
from fstg.helpers import button, cache
from fstg.utils import config

if TYPE_CHECKING:
    from hydrogram.types import CallbackQuery

    from fstg.base import Bot


@Client.on_callback_query(filter_authorized & filters.regex(r"\bcancel\b"))
async def cancel_handler_query(client: "Bot", callback_query: "CallbackQuery") -> None:
    chat_id, user_id = callback_query.message.chat.id, callback_query.from_user.id
    await client.stop_listening(chat_id=chat_id, user_id=user_id)


@Client.on_callback_query(filter_authorized & filters.regex(r"\bsettings\b"))
async def settings_handler_query(_: "Bot", callback_query: "CallbackQuery") -> None:
    await callback_query.message.edit_text(
        "<pre language='Bot Settings'>List Available Menu</pre>",
        reply_markup=ikb(button.Menu),
    )


@Client.on_callback_query(filters.regex(r"\bclose\b"))
async def close_handler_query(_: "Bot", callback_query: "CallbackQuery") -> None:
    message = callback_query.message

    if message.reply_to_message_id:
        await message.reply_to_message.delete()

    await message.delete()


@Client.on_callback_query(
    filter_authorized & filters.regex(r"menu_(generate|protect|start|admins|fsubs)")
)
async def menu_handler_query(_: "Bot", callback_query: "CallbackQuery") -> None:
    def format_list_items(item_title: str, list_items: List[int]) -> str:
        formatted_items = (
            "\n".join(
                f"{i + 1}. <code>{item}</code>" for i, item in enumerate(list_items)
            )
            if list_items
            else "None"
        )
        return f"<blockquote><b>{item_title}</b>\n{formatted_items}</blockquote>"

    callback_query_data = callback_query.data.split("_")[1]
    response_texts = {
        "generate": f"<pre language='Generate Status'>{cache.generate_status}</pre>",
        "protect": f"<pre language='Protect Content'>{cache.protect_content}</pre>",
        "start": f"<pre language='Start Text Message'>{cache.start_text}</pre>",
        "admins": format_list_items("List Bot Admins", cache.admins),
        "fsubs": format_list_items("List Bot F-Subs", cache.fs_chats),
    }

    if callback_query_data in response_texts:
        await callback_query.message.edit_text(
            response_texts[callback_query_data],
            reply_markup=ikb(getattr(button, callback_query_data.capitalize(), [])),
        )


@Client.on_callback_query(
    filter_authorized & filters.regex(r"switch_(generate|protect)")
)
async def switch_handler_query(_: "Bot", callback_query: "CallbackQuery") -> None:
    callback_query_data = callback_query.data.split("_")[1]

    if callback_query_data == "generate":
        await update_generate_status()
        await cache.generate_status_init()
        text = (
            f"<pre language='Generate Status'>Switched to {cache.generate_status}</pre>"
        )

    else:
        await update_protect_content()
        await cache.protect_content_init()
        text = (
            f"<pre language='Protect Content'>Switched to {cache.protect_content}</pre>"
        )

    await callback_query.message.edit_text(text, reply_markup=ikb(button.Back))


@Client.on_callback_query(filter_authorized & filters.regex(r"custom_start"))
async def custom_start_handler_query(
    client: "Bot", callback_query: "CallbackQuery"
) -> None:
    await callback_query.message.edit_text(
        "<blockquote><b>Send Custom Start Text Message!</b></blockquote>\n"
        "<pre language=Timeout>45 Seconds</pre>",
        reply_markup=ikb(button.Cancel),
    )

    chat_id, user_id = callback_query.message.chat.id, callback_query.from_user.id
    buttons = ikb(button.Back)

    try:
        listening = await client.listen(chat_id=chat_id, user_id=user_id, timeout=45)
        new_text = listening.text
        await listening.delete()
    except ListenerStopped:
        await callback_query.message.edit_text(
            "<blockquote><b>Process Cancelled!</b></blockquote>", reply_markup=buttons
        )
        return
    except ListenerTimeout:
        await callback_query.message.edit_text(
            "<pre language=Timeout>Process Cancelled!</pre>", reply_markup=buttons
        )
        return

    if not new_text:
        await callback_query.message.edit_text(
            "<pre language='Format Invalid'>Just Send Text!</pre>", reply_markup=buttons
        )
    else:
        await update_start_text_message(new_text)
        await cache.start_text_init()

        await callback_query.message.edit_text(
            f"<pre language='Start Text Message Customized'>{new_text}</pre>",
            reply_markup=buttons,
        )


@Client.on_callback_query(filter_authorized & filters.regex(r"add_(admin|f-sub|channel-db)"))
async def add_handler_query(client: "Bot", callback_query: "CallbackQuery") -> None:
    callback_query_data = callback_query.data.split("_")[1]
    channel_mode = callback_query_data.startswith("channel")
    entity_data = (
        "User ID" if callback_query_data == "admin"
        else "Chat ID" if callback_query_data == "f-sub"
        else "Stored Database Channel ID"
    )
    await callback_query.message.edit_text(
        f"<blockquote><b>Send a {entity_data} to Add {callback_query_data.title()}!</b></blockquote>\n"
        "<pre language=Timeout>45 Seconds</pre>",
        reply_markup=ikb(button.Cancel),
    )

    chat_id, user_id = callback_query.message.chat.id, callback_query.from_user.id
    buttons = ikb(button.Back)
    if channel_mode:
        buttons = ikb([[("« Back to Profile", "profile")]])

    try:
        listening = await client.listen(chat_id=chat_id, user_id=user_id, timeout=45)
        await listening.delete()

        if not listening.text:
            raise ValueError

        new_id = int(listening.text)
    except ListenerStopped:
        await callback_query.message.edit_text(
            "<blockquote><b>Process Cancelled!</b></blockquote>", reply_markup=buttons
        )
        return
    except ListenerTimeout:
        await callback_query.message.edit_text(
            "<pre language=Timeout>Process Cancelled!</pre>", reply_markup=buttons
        )
        return
    except ValueError:
        await callback_query.message.edit_text(
            f"<pre language='Format Invalid'>Just Send {entity_data}!</pre>",
            reply_markup=buttons,
        )
        return

    list_ids = cache.admins if callback_query_data == "admin" else cache.fs_chats
    if new_id in list_ids:
        await callback_query.message.edit_text(
            f"<blockquote><b>{entity_data} Already Added!</b></blockquote>",
            reply_markup=buttons,
        )
        return

    try:
        chat = await client.get_chat(new_id)
        if (callback_query_data == "admin" and chat.type != ChatType.PRIVATE) or \
            (callback_query_data == "fsub" and chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL]) or \
            (channel_mode and chat.type != ChatType.CHANNEL
        ):
            raise Exception
    except Exception:
        await callback_query.message.edit_text(
            f"<blockquote><b>{entity_data} Invalid!</b></blockquote>",
            reply_markup=buttons,
        )
        return

    if callback_query_data == "admin":
        await add_admin(new_id)
        await cache.admins_init()
    elif channel_mode:
        config.DATABASE_CHAT_ID = new_id
    else:
        await add_fs_chat(new_id)
        await cache.fs_chats_init()

    await callback_query.message.edit_text(
        f"<pre language='{callback_query_data.title()} Added'>{entity_data}: {new_id}</pre>",
        reply_markup=buttons,
    )


@Client.on_callback_query(filter_authorized & filters.regex(r"del_(admin|f-sub)"))
async def del_handler_query(client: "Bot", callback_query: "CallbackQuery") -> None:
    callback_query_data = callback_query.data.split("_")[1]
    entity_data = "User ID" if callback_query_data == "admin" else "Chat ID"
    await callback_query.message.edit_text(
        f"<blockquote><b>Send {entity_data} to Delete {callback_query_data.title()}!</b></blockquote>\n"
        "<pre language=Timeout>45 Seconds</pre>",
        reply_markup=ikb(button.Cancel),
    )

    chat_id, user_id = callback_query.message.chat.id, callback_query.from_user.id
    buttons = ikb(button.Back)

    try:
        listening = await client.listen(chat_id=chat_id, user_id=user_id, timeout=45)
        await listening.delete()

        if not listening.text:
            raise ValueError

        get_id = int(listening.text)
    except ListenerStopped:
        await callback_query.message.edit_text(
            "<blockquote><b>Process Cancelled!</b></blockquote>", reply_markup=buttons
        )
        return
    except ListenerTimeout:
        await callback_query.message.edit_text(
            "<pre language=Timeout>Process Cancelled!</pre>", reply_markup=buttons
        )
        return
    except ValueError:
        await callback_query.message.edit_text(
            f"<pre language='Format Invalid'>Just Send {entity_data}!</pre>",
            reply_markup=buttons,
        )
        return

    list_ids = cache.admins if callback_query_data == "admin" else cache.fs_chats
    if get_id not in list_ids:
        await callback_query.message.edit_text(
            f"<blockquote><b>{entity_data} Invalid!</b></blockquote>",
            reply_markup=buttons,
        )
        return

    if callback_query_data == "admin":
        if get_id == user_id:
            await callback_query.message.edit_text(
                "<blockquote><b>That's Yours!</b></blockquote>", reply_markup=buttons
            )
            return

        if user_id == config.OWNER_ID or list_ids.index(user_id) < list_ids.index(
            get_id
        ):
            await del_admin(get_id)
            await cache.admins_init()
        else:
            await callback_query.message.edit_text(
                "<blockquote><b>Can't Delete Higher!</b></blockquote>",
                reply_markup=buttons,
            )
            return
    else:
        await del_fs_chat(get_id)
        await cache.fs_chats_init()

    await callback_query.message.edit_text(
        f"<pre language='{callback_query_data.title()} Deleted'>{entity_data}: {get_id}</pre>",
        reply_markup=buttons,
    )
