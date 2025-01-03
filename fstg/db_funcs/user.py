from typing import Any, Dict, List, Optional

from fstg.base import database
from fstg.utils import config


async def add_user(user_id: int) -> None:
    await database.add_value(int(config.BOT_ID), "BOT_USERS", user_id)


async def del_user(user_id: int) -> None:
    await database.del_value(int(config.BOT_ID), "BOT_USERS", user_id)


async def get_users() -> List[int]:
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    return (
        doc.get("BOT_USERS", [])
        if doc and isinstance(doc.get("BOT_USERS"), list)
        else []
    )
