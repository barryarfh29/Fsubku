import datetime
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.API_ID = int(os.getenv("API_ID", 2040))
        self.API_HASH: str = os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627")
        self.OWNER_ID = int(os.getenv("OWNER_ID", 1913880001))
        self.SUPPORT_URL: str = os.getenv("SUPPORT_URL", "t.me/TermuxExecute")
        self.BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN", None)
        self.DATABASE_CHAT_ID: Optional[int] = int(os.getenv("DATABASE_CHAT_ID", 0))
        self.MONGODB_URL: Optional[str] = os.getenv(
            "MONGODB_URL", "mongodb://root:passwd@mongo:27017"
        )
        self.EXPIRED_DATE: Optional[str] = os.getenv("EXPIRED_DATE", None)
        self.DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"

        self._validate_vars()
        self._validate_opt()
        self.BOT_ID = self._parse_id(self.BOT_TOKEN)

    def _parse_id(self, bot_token: Optional[str]) -> Optional[str]:
        if bot_token and ":" in bot_token:
            return bot_token.split(":", 1)[0]
        return None

    def _validate_vars(self):
        required_vars = {
            "API_ID": self.API_ID,
            "API_HASH": self.API_HASH,
            "OWNER_ID": self.OWNER_ID,
            "SUPPORT_URL": self.SUPPORT_URL,
            "BOT_TOKEN": self.BOT_TOKEN,
            "DATABASE_CHAT_ID": self.DATABASE_CHAT_ID,
            "MONGODB_URL": self.MONGODB_URL,
        }
        for var_name, value in required_vars.items():
            if value is None or (isinstance(value, int) and value == 0):
                logger.error(f"{var_name} is None or invalid", exc_info=False)

    def _validate_opt(self):
        if self.EXPIRED_DATE:
            try:
                datetime.datetime.strptime(self.EXPIRED_DATE, "%Y/%m/%d")
            except ValueError:
                logger.error("EXPIRED_DATE is invalid", exc_info=False)


config: Config = Config()
