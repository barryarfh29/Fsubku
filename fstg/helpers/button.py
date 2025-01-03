import contextlib
from typing import TYPE_CHECKING, List, Optional, Tuple

from hydrogram.helpers import ikb

from fstg.utils import config

from .cache import cache

if TYPE_CHECKING:
    from hydrogram import Client
    from hydrogram.types import Message

from typing import List, Tuple


class Button:
    Help = [[("« Back", "start"), ("Support", config.SUPPORT_URL, "url")]]
    Close = [[("Close", "close")]]
    BcStop = [[("Stop", "broadcast_stop")]]
    BcStats = [
        [("Refresh Status", "broadcast_refresh")],
        [("Stop", "broadcast_stop"), ("Close", "close")],
    ]
    Abort = [[("Abort", "cmd_abort")]]
    Eval = [[("Refresh", "cmd_eval")]]
    Shell = [[("Refresh", "cmd_shell")]]
    Menu = [
        [("Generate", "menu_generate"), ("Protect", "menu_protect")],
        [("Custom Start Text", "menu_start")],
        [("Admins", "menu_admins"), ("F-Subs", "menu_fsubs")],
        [("« Back to Start", "start")],
    ]
    Back = [[("« Back to Menu", "settings")]]
    Cancel = [[("Cancel", "cancel")]]
    Generate = [[("Switch", "switch_generate")], [("« Back", "settings")]]
    Start = [[("« Back", "settings"), ("Custom", "custom_start")]]
    Protect = [[("Switch", "switch_protect")], [("« Back", "settings")]]
    Admins = [
        [("Add", "add_admin"), ("Del", "del_admin")],
        [("« Back to Menu", "settings")],
    ]
    Fsubs = [
        [("Add", "add_f-sub"), ("Del", "del_f-sub")],
        [("« Back to Menu", "settings")],
    ]


button: Button = Button()


def admin_buttons() -> ikb:
    buttons: List[Tuple[str, str, str]] = []
    fs_data = cache.fs_chats
    if fs_data:
        for i, (_, chat_info) in enumerate(fs_data.items()):
            chat_type = chat_info.get("chat_type", "Unknown")
            invite_link = chat_info.get("invite_link", "#")
            buttons.append((f"{i + 1}. {chat_type}", invite_link, "url"))

    button_layouts = fmt_row_buttons(buttons)
    button_layouts.append(
        [("Profile", "profile"), ("Help", "help"), ("Settings", "settings")]
    )

    return ikb(button_layouts)


async def join_buttons(
    client: "Client", message: "Message", user_id: int
) -> Optional[ikb]:
    async def user_is_not_join() -> Optional[List[int]]:
        chat_ids = list(cache.fs_chats.keys())
        if not chat_ids or user_id in cache.admins or user_id == config.OWNER_ID:
            return None

        already_joined = set()
        for chat_id in chat_ids:
            with contextlib.suppress(Exception):
                await client.get_chat_member(chat_id, user_id)
                already_joined.add(chat_id)

        return [chat_id for chat_id in chat_ids if chat_id not in already_joined]

    no_join_ids = await user_is_not_join()
    if not no_join_ids:
        return None

    buttons: List[Tuple[str, str, str]] = []
    fs_data = cache.fs_chats
    for chat_id in no_join_ids:
        chat_info = fs_data.get(chat_id, {})
        chat_type = chat_info.get("chat_type", "Unknown")
        invite_link = chat_info.get("invite_link", "#")
        buttons.append((f"Join {chat_type}", invite_link, "url"))

    button_layouts = fmt_row_buttons(buttons)
    if len(message.command) > 1:
        start_url = f"https://t.me/{client.me.username}?start={message.command[1]}"
        button_layouts.append([("Try Again", start_url, "url")])

    return ikb(button_layouts)


def fmt_row_buttons(
    buttons: List[Tuple[str, str, str]], rows: int = 2
) -> List[List[Tuple[str, str, str]]]:
    return [buttons[i : i + rows] for i in range(0, len(buttons), rows)]
