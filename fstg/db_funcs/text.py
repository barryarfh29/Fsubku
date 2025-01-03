from typing import Any, Dict, Optional

from fstg.base import database
from fstg.utils import config


async def add_start_text_message(value: str) -> None:
    await database.add_value(int(config.BOT_ID), "START_TEXT", value)


async def del_start_text_message() -> None:
    await database.clear_value(int(config.BOT_ID), "START_TEXT")


async def get_start_text_message() -> str:
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    return doc.get("START_TEXT", ["#"])[0] if doc else "#"


async def update_start_text_message(value: str) -> None:
    await del_start_text_message()
    await add_start_text_message(value)
