from typing import TYPE_CHECKING

from hydrogram import filters
from hydrogram.enums import ChatType
from hydrogram.types import Message

from fstg.helpers import cache
from fstg.utils import config

if TYPE_CHECKING:
    from hydrogram import Client
    from hydrogram.filters import Filter


def generate(_: "Filter", __: "Client", message: Message) -> bool:
    if not cache.generate_status:
        return False

    if message.from_user is None:
        return False

    user_id = message.from_user.id

    if message.chat.type == ChatType.PRIVATE:
        if user_id in cache.admins or user_id == config.OWNER_ID:
            return True

    return False


filter_generate = filters.create(generate, name="filter_generate")
