import datetime
from typing import Optional

from .config import config
from .misc import convert_seconds, decode_data, paste_content, url_safe

expired_date: Optional[datetime.datetime] = None
if config.EXPIRED_DATE:
    expired_date = datetime.datetime.strptime(config.EXPIRED_DATE, "%Y/%m/%d")

__all__ = [
    "config",
    "convert_seconds",
    "decode_data",
    "paste_content",
    "url_safe",
    "expired_date",
]
