import asyncio
from typing import TYPE_CHECKING, Union

from hydrogram import Client, filters
from hydrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from hydrogram.helpers import ikb

from fstg.db_funcs import del_user, get_users
from fstg.filters import filter_broadcast
from fstg.helpers import button, cache
from fstg.utils import config, convert_seconds

if TYPE_CHECKING:
    from hydrogram.types import CallbackQuery, Message

    from fstg.base import Bot


class BroadcastManager:
    def __init__(self):
        self.is_running: bool = False
        self.sent: int = 0
        self.failed: int = 0
        self.total: int = 0
        self.start_time: Union[int, float] = 0

    def get_elapsed_time(self, client: "Bot") -> str:
        elapsed_time = client.loop.time() - self.start_time

        return convert_seconds(elapsed_time)

    def get_estimated_time(self, client: "Bot") -> str:
        if self.sent == 0:
            return "None"

        avg_time_per_message = (client.loop.time() - self.start_time) / self.sent
        remaining_messages = self.total - (self.sent + self.failed)
        estimated_time = avg_time_per_message * remaining_messages

        return convert_seconds(estimated_time)

    async def start_broadcast(
        self, client: "Bot", message: "Message", broadcast_message: "Message"
    ) -> None:
        if self.is_running:
            await message.reply_text(
                "<blockquote><b>Broadcast is Running!</b></blockquote>",
                quote=True,
                reply_markup=ikb([[("Status", "broadcast_refresh")]]),
            )
            return

        progress_message = await message.reply_text(
            "<blockquote><b>Broadcasting...</b></blockquote>",
            quote=True,
            reply_markup=ikb(button.BcStop),
        )

        admin_ids = cache.admins + [config.OWNER_ID]
        all_users = await get_users()

        user_ids = [user_id for user_id in all_users if user_id not in admin_ids]

        self.is_running, self.total = True, len(user_ids)
        self.start_time = client.loop.time()

        for user_id in user_ids:
            if not self.is_running:
                break

            try:
                await broadcast_message.copy(
                    user_id, protect_content=cache.protect_content
                )
                self.sent += 1
            except FloodWait as wait:
                await asyncio.sleep(wait.value)
                await broadcast_message.copy(
                    user_id, protect_content=cache.protect_content
                )
                self.sent += 1
            except (InputUserDeactivated, PeerIdInvalid, UserIsBlocked):
                await del_user(user_id)
                self.failed += 1
            except Exception:
                self.failed += 1

            if (self.sent + self.failed) % 250 == 0:
                await self.update_progress(client, progress_message)

        await self.finalize_broadcast(client, progress_message)

    async def update_progress(self, client: "Bot", message: "Message") -> None:
        elapsed_time = self.get_elapsed_time(client)
        estimated_time = self.get_estimated_time(client)
        await message.edit_text(
            "<pre language='Broadcast Status'>"
            f"Sent {self.sent} from {self.total}</pre>\n"
            f"<pre language=Failed>{self.failed}</pre>\n"
            f"<pre language='Elapsed Time'>{elapsed_time}</pre>\n"
            f"<pre language='Estimated Time'>{estimated_time}</pre>",
            reply_markup=ikb(button.BcStop),
        )

    async def finalize_broadcast(self, client: "Bot", message: "Message") -> None:
        status_message = (
            "Broadcast Finished"
            if self.sent + self.failed == self.total
            else "Broadcast Stopped"
        )

        elapsed_time = self.get_elapsed_time(client)
        await message.reply_text(
            f"<pre language='{status_message}'>"
            f"Sent {self.sent} from {self.total}</pre>\n"
            f"<pre language=Failed>{self.failed}</pre>\n"
            f"<pre language='Elapsed Time'>{elapsed_time}</pre>",
            reply_to_message_id=message.reply_to_message_id,
            reply_markup=ikb(button.Close),
        )

        await message.delete()

        self.is_running = False
        self.sent, self.failed, self.total, self.start_time = 0, 0, 0, 0


broadcast_manager = BroadcastManager()


@Client.on_message(filter_broadcast & filters.command("bcast"))
async def broadcast_handler(client: "Bot", message: "Message") -> None:
    broadcast_message = message.reply_to_message

    if not broadcast_message:
        if not broadcast_manager.is_running:
            await message.reply_text(
                "<blockquote><b>Reply to Message!</b></blockquote>", quote=True
            )
        else:
            elapsed_time = broadcast_manager.get_elapsed_time(client)
            estimated_time = broadcast_manager.get_estimated_time(client)
            await message.reply_text(
                "<pre language='Broadcast Status'>"
                f"Sent {broadcast_manager.sent} from {broadcast_manager.total}</pre>\n"
                f"<pre language=Failed>{broadcast_manager.failed}</pre>\n"
                f"<pre language='Elapsed Time'>{elapsed_time}</pre>\n"
                f"<pre language='Estimated Time'>{estimated_time}</pre>",
                quote=True,
                reply_markup=ikb(button.BcStats),
            )
        return

    await broadcast_manager.start_broadcast(client, message, broadcast_message)


@Client.on_callback_query(filter_broadcast & filters.regex(r"broadcast_(refresh|stop)"))
async def stop_broadcast_handler_query(
    client: "Bot", callback_query: "CallbackQuery"
) -> None:
    callback_query_data = callback_query.data.split("_")[1]

    if callback_query_data == "stop":
        broadcast_manager.is_running = False

        await callback_query.message.edit_text(
            "<blockquote><b>Broadcast Stopped!</b></blockquote>"
        )
    else:
        await callback_query.message.edit_text(
            "<blockquote><b>Refreshing...</b></blockquote>"
        )
        if broadcast_manager.is_running:
            elapsed_time = broadcast_manager.get_elapsed_time(client)
            estimated_time = broadcast_manager.get_estimated_time(client)
            await callback_query.message.edit_text(
                "<pre language='Broadcast Status'>"
                f"Sent {broadcast_manager.sent} from {broadcast_manager.total}</pre>\n"
                f"<pre language=Failed>{broadcast_manager.failed}</pre>\n"
                f"<pre language='Elapsed Time'>{elapsed_time}</pre>\n"
                f"<pre language='Estimated Time'>{estimated_time}</pre>",
                reply_markup=ikb(button.BcStats),
            )
        else:
            await callback_query.message.edit_text(
                "<blockquote><b>No Broadcast is Running!</b></blockquote>",
                reply_markup=ikb(button.Close),
            )
