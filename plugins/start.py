import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Union

from hydrogram import Client, filters, types
from hydrogram.helpers import ikb
from hydrogram.types import WebAppInfo

from fstg.db_funcs import add_user
from fstg.filters import filter_authorized
from fstg.helpers import admin_buttons, button, cache, join_buttons
from fstg.utils import config, decode_data, expired_date

if TYPE_CHECKING:
    from hydrogram.types import CallbackQuery, Message, User

    from fstg.base import Bot


@Client.on_callback_query(filter_authorized & filters.regex(r"\bstart\b"))
async def start_handler_query(_: "Bot", callback_query: "CallbackQuery") -> None:
    user, reply_markup = callback_query.from_user, admin_buttons()

    await reply_message_text(event=callback_query, user=user, reply_markup=reply_markup)


@Client.on_callback_query(filter_authorized & filters.regex(r"\bhelp\b"))
async def help_handler_query(client: "Bot", callback_query: "CallbackQuery") -> None:
    await callback_query.message.edit_text(
        "<pre language='Available Commands'>"
        "/batch: Generate URL for Multi Message\n"
        "/bcast: Broadcast by Reply to Message\n"
        "/users: Total of Bot Users</pre>\n"
        '<pre language=Note>More Commands, Type "/"</pre>',
        reply_markup=ikb(button.Help),
    )


@Client.on_callback_query(filter_authorized & filters.regex(r"\bprofile\b"))
async def profile_handler_query(_: "Bot", callback_query: "CallbackQuery") -> None:
    expired_date_str = None
    if expired_date:
        expired_date_str = expired_date.strftime("%B %d, %Y")
    await callback_query.message.edit_text(
        f"<pre language='Bot ID'><code>{config.BOT_ID}</pre>\n"
        f"<pre language='Database Channel'>{config.DATABASE_CHAT_ID}</pre>\n"
        f"<pre language='Expired Date'>{expired_date_str}</pre>",
        reply_markup=ikb([[("« Back to Start", "start")]]),
    )


@Client.on_message(filters.private & filters.command("start"))
async def start_handler(client: "Bot", message: "Message") -> None:
    user = message.from_user

    if user.id != config.OWNER_ID:
        await add_user(user.id)

    user_buttons = await join_buttons(client, message, user.id)
    list_of_admins = cache.admins + [config.OWNER_ID]

    if len(message.command) > 1:
        if user_buttons:
            return await reply_message_text(
                event=message, user=user, reply_markup=user_buttons
            )

        message_ids = decode_data(message.command[1])
        messages = await client.get_messages(config.DATABASE_CHAT_ID, message_ids)
        for content in messages:
            if content.empty:
                continue
            else:
                await content.copy(user.id, protect_content=cache.protect_content)
                await asyncio.sleep(0.25)
    else:
        buttons = admin_buttons() if user.id in list_of_admins else user_buttons
        await reply_message_text(event=message, user=user, reply_markup=buttons)


@Client.on_message(filters.private & filters.command("privacy"))
async def privacy_handler(_: "Bot", message: "Message") -> None:
    privacy_policy: str = """
<b>Last Updated: July 04, 2024</b>

This Privacy Policy explains how we collect, use, and protect your information when you use our bot.

<b>1. Information We Collect</b>
<blockquote><b>1.1 Personal Information</b>
- We do not collect any personal information such as your name, email address, or phone number.

<b>1.2 Usage Data</b>
- We may collect information about your interactions with the bot, such as messages sent, commands used, and the time and date of your interactions.</blockquote>

<b>2. How We Use Your Information</b>
<blockquote><b>2.1 To Operate the Bot</b>
- The information collected is used to operate and improve the functionality of the bot.

<b>2.2 To Improve Our Services</b>
- We may use the information to analyze how users interact with the bot in order to improve our services.</blockquote>

<b>3. Data Security</b>
<blockquote><b>3.1 Security Measures</b>
- We implement appropriate technical and organizational measures to protect your information from unauthorized access, disclosure, alteration, or destruction.</blockquote>

<b>4. Data Sharing and Disclosure</b>
<blockquote><b>4.1 Third-Party Services</b>
- We do not share your information with third parties, except as required by law or to protect our rights.</blockquote>

<b>5. Your Data Protection Rights</b>
<blockquote><b>5.1 Access and Control</b>
- You have the right to request access to the information we have collected about you. You also have the right to request that we correct or delete your data.</blockquote>

<b>6. Changes to This Privacy Policy</b>
<blockquote><b>6.1 Updates</b>
- We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.</blockquote>

<b>Note:</b>
<blockquote>- It's important to review this policy with a legal professional to ensure compliance with relevant laws and regulations.</blockquote>
"""
    # <b>7. Contact Us</b>
    # <blockquote><b>7.1 Contact Information</b>
    # - If you have any questions about this Privacy Policy, please contact us on the button below.</blockquote>

    await message.reply_text(
        privacy_policy,
        quote=True,
        reply_markup=ikb(
            [
                [
                    (
                        "Standard Bot Privacy Policy",
                        WebAppInfo(url="https://telegram.org/privacy-tpa"),
                        "web_app",
                    )
                ]
            ]
        ),
    )


async def reply_message_text(
    event: Union[types.CallbackQuery, types.Message], user: "User", reply_markup: "ikb"
) -> None:
    start_text = format_text_message(cache.start_text, user)
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(start_text, reply_markup=reply_markup)
    else:
        await event.reply_text(start_text, quote=True, reply_markup=reply_markup)


def format_text_message(text: str, user: "User") -> str:
    first_name, last_name = user.first_name, user.last_name
    full_name = f"{first_name} {last_name}".strip() if last_name else first_name

    user_data = defaultdict(
        lambda: "{}",
        {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "mention": user.mention(full_name),
        },
    )

    return text.format_map(user_data)
