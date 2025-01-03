from typing import TYPE_CHECKING

from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.raw.functions import Ping

from fstg.helpers import button

if TYPE_CHECKING:
    from hydrogram.types import Message

    from fstg.base import Bot


@Client.on_message(filters.private & filters.command("ping"))
async def ping_handler(client: "Bot", message: "Message") -> None:
    latency = await ping_function(client)

    await message.reply_text(
        f"<pre language=Latency>{latency}</pre>",
        quote=True,
        reply_markup=ikb(button.Close),
    )


async def ping_function(client: "Bot") -> str:
    start_time = client.loop.time()
    await client.invoke(Ping(ping_id=client.rnd_id()))

    latency_ms = (client.loop.time() - start_time) * 1000
    return f"{int(latency_ms)} ms"
