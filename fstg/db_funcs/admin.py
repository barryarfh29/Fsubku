from typing import Any, Dict, List, Optional

from fstg.base import database
from fstg.utils import config


async def add_admin(chat_id: int) -> None:
    await database.add_value(int(config.BOT_ID), "BOT_ADMINS", chat_id)


async def del_admin(chat_id: int) -> None:
    await database.del_value(int(config.BOT_ID), "BOT_ADMINS", chat_id)


async def get_admins() -> List[int]:
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    return (
        doc.get("BOT_ADMINS", [])
        if doc and isinstance(doc.get("BOT_ADMINS"), list)
        else []
    )
