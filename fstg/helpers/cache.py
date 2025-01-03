from typing import TYPE_CHECKING, Dict, List

from hydrogram.enums import ChatType, UserStatus

from fstg.base import Bot
from fstg.db_funcs import (
    del_admin,
    del_fs_chat,
    get_admins,
    get_fs_chats,
    get_generate_status,
    get_protect_content,
    get_start_text_message,
)

if TYPE_CHECKING:
    from hydrogram import Client


class Cache:
    def __init__(self, client: "Client") -> None:
        self.client = client
        self.start_text: str = "<blockquote><b>Initializing...</b></blockquote>"
        self.admins: List[int] = []
        self.fs_chats: Dict[int, Dict[str, str]] = {}
        self.protect_content: bool = False
        self.generate_status: bool = False

    async def start_text_init(self) -> str:
        self.start_text = await get_start_text_message()
        return self.start_text

    async def admins_init(self) -> List[int]:
        self.admins.clear()

        admin_ids = await get_admins()
        for admin_id in admin_ids:
            try:
                admin = await self.client.get_users(admin_id)
                if admin.is_deleted or admin.status == UserStatus.LONG_AGO:
                    raise Exception
                else:
                    self.admins.append(admin_id)
            except Exception:
                await del_admin(admin_id)

        return self.admins

    async def fs_chats_init(self) -> Dict[int, Dict[str, str]]:
        self.fs_chats.clear()

        fs_chats = await get_fs_chats()
        for i, chat_id in enumerate(fs_chats):
            try:
                chat = await self.client.get_chat(chat_id=chat_id)
                chat_type = (
                    "Group"
                    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
                    else "Channel"
                )
                invite_link = chat.invite_link
                if not invite_link:
                    raise Exception

                self.fs_chats[chat_id] = {
                    "chat_type": chat_type,
                    "invite_link": invite_link,
                }
            except Exception:
                await del_fs_chat(chat_id)

        return self.fs_chats

    async def protect_content_init(self) -> bool:
        self.protect_content = await get_protect_content()
        return self.protect_content

    async def generate_status_init(self) -> bool:
        self.generate_status = await get_generate_status()
        return self.generate_status


cache: Cache = Cache(Bot)
