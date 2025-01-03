from typing import TYPE_CHECKING, Union

from hydrogram import filters
from hydrogram.enums import ChatType
from hydrogram.types import CallbackQuery, Message

from fstg.helpers import cache
from fstg.utils import config

if TYPE_CHECKING:
    from hydrogram import Client
    from hydrogram.filters import Filter


def broadcast(_: "Filter", __: "Client", event: Union[CallbackQuery, Message]) -> bool:
    message = event.message if isinstance(event, CallbackQuery) else event

    if event.from_user is None:
        return False

    user_id = event.from_user.id

    if message.chat.type in [ChatType.PRIVATE, ChatType.SUPERGROUP]:
        if user_id in cache.admins or user_id == config.OWNER_ID:
            return True

    return False


filter_broadcast = filters.create(broadcast, name="filter_broadcast")
