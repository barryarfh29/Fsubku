from fstg.base import database
from fstg.utils import config


async def initial_database() -> None:
    default_start_text = (
        "Hello, {mention}!\n\n"
        "The bot is up and running. These bots can store messages in custom chats, "
        "and users access them through the bot.\n\n"
        "To view messages shared by bots, join first, then press the Try Again button."
    )

    bot_id = int(config.BOT_ID)

    doc = await database.get_doc(bot_id)
    key = "START_TEXT"
    if not doc or key not in doc:
        await database.add_value(bot_id, key, default_start_text)
