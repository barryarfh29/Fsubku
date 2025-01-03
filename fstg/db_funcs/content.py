from typing import Any, Dict, Optional

from fstg.base import database
from fstg.utils import config


async def add_generate_status(value: bool) -> None:
    await database.add_value(int(config.BOT_ID), "GENERATE_URL", value)


async def del_generate_status() -> None:
    await database.clear_value(int(config.BOT_ID), "GENERATE_URL")


async def get_generate_status() -> bool:
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    return doc.get("GENERATE_URL", [True])[0]


async def update_generate_status() -> None:
    current_generate_status = await get_generate_status()
    await del_generate_status()
    await add_generate_status(not current_generate_status)


async def add_protect_content(value: bool) -> None:
    await database.add_value(int(config.BOT_ID), "PROTECT_CONTENT", value)


async def del_protect_content() -> None:
    await database.clear_value(int(config.BOT_ID), "PROTECT_CONTENT")


async def get_protect_content() -> bool:
    doc: Optional[Dict[str, Any]] = await database.get_doc(int(config.BOT_ID))
    return doc.get("PROTECT_CONTENT", [True])[0]


async def update_protect_content() -> None:
    current_protect_content_status = await get_protect_content()
    await del_protect_content()
    await add_protect_content(not current_protect_content_status)
