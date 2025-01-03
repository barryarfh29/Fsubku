import asyncio
import contextlib
import datetime
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from hydrogram.helpers import ikb

from fstg.base import Bot
from fstg.db_funcs import initial_database
from fstg.helpers import cache
from fstg.utils import config, expired_date

logging.basicConfig(format="%(name)s - %(message)s", level=logging.INFO)

for lib in {"aiohttp", "apscheduler", "hydrogram", "pymongo"}:
    if config.DEBUG_MODE:
        logging.getLogger(lib).setLevel(logging.WARNING)
    else:
        logging.getLogger(lib).setLevel(logging.CRITICAL)

logger = logging.getLogger(config.BOT_ID)


async def expired_date_init() -> None:
    async def send_message_to_admins(message_text: str) -> None:
        reply_markup = ikb([[("Renew", config.SUPPORT_URL, "url")]])
        for admin in cache.admins:
            with contextlib.suppress(Exception):
                await Bot.send_message(
                    chat_id=admin, text=message_text, reply_markup=reply_markup
                )
            await asyncio.sleep(0.25)

    current_date = datetime.datetime.now()
    if expired_date <= current_date:
        await send_message_to_admins("<blockquote><b>Bot Expired!</b></blockquote>")

        Bot.loop.stop()


async def main() -> None:
    await Bot.start()

    await initial_database()

    await asyncio.gather(
        cache.start_text_init(),
        cache.generate_status_init(),
        cache.protect_content_init(),
        cache.admins_init(),
        cache.fs_chats_init(),
    )

    logger_message = ""
    if expired_date:
        logger_message += f"{config.EXPIRED_DATE} - "
        await expired_date_init()

        scheduler = AsyncIOScheduler()
        scheduler.add_job(expired_date_init, trigger="cron", minute=45, hour=9)
        scheduler.start()

    logger_message += f"t.me/{Bot.me.username}"
    logger.info(logger_message)


if __name__ == "__main__":
    loop = Bot.loop

    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except BaseException:
        pass
    finally:
        loop.run_until_complete(Bot.stop())
