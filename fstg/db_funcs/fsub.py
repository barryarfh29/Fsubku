from typing import Any, Dict, List, Optional

from fstg.base import database
from fstg.utils import config


async def add_fs_chat(chat_id: int) -> None:
    await database.add_value(int(config.BOT_ID), "FSUB_CHATS", chat_id)


async def del_fs_chat(chat_id: int) -> None:
    await database.del_value(int(config.BOT_ID), "FSUB_CHATS", chat_id)


async def get_fs_chats() -> List[int]:
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    return (
        doc.get("FSUB_CHATS", [])
        if doc and isinstance(doc.get("FSUB_CHATS"), list)
        else []
    )
