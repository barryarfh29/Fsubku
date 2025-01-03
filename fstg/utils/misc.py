import base64
from typing import List, Optional, Union

from aiohttp import ClientSession

from .config import config


class URLSafe:
    @staticmethod
    def add_padding(data_string: str) -> str:
        return data_string + "=" * (-len(data_string) % 4)

    @staticmethod
    def del_padding(data_string: str) -> str:
        return data_string.rstrip("=")

    def encode_data(self, data: str) -> str:
        data_bytes = data.encode("utf-8")
        encoded_data = base64.urlsafe_b64encode(data_bytes)
        return self.del_padding(encoded_data.decode("utf-8"))

    def decode_data(self, data_string: str) -> Optional[str]:
        data_padding = self.add_padding(data_string)
        encoded_data = base64.urlsafe_b64decode(data_padding)
        return encoded_data.decode("utf-8")


url_safe: URLSafe = URLSafe()


def convert_seconds(seconds: Union[int, float]) -> str:
    weeks, remainder = divmod(seconds, 7 * 24 * 60 * 60)
    days, remainder = divmod(remainder, 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, seconds = divmod(remainder, 60)

    result_converted = []
    if weeks > 0:
        result_converted.append(f"{int(weeks)} Week{'s' if weeks > 1 else ''}")
    if days > 0:
        result_converted.append(f"{int(days)} Day{'s' if days > 1 else ''}")
    if hours > 0:
        result_converted.append(f"{int(hours)} Hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        result_converted.append(f"{int(minutes)} Minute{'s' if minutes > 1 else ''}")
    if seconds >= 1:
        result_converted.append(
            f"{int(seconds)} Second{'s' if int(seconds) > 1 else ''}"
        )
    elif seconds > 0:
        result_converted.append(
            f"{'{:.3f}'.format(seconds).rstrip('0').rstrip('.')} Seconds"
        )

    return ", ".join(result_converted[:3])


def decode_data(encoded_data: str) -> Union[List[int], range]:
    database_chat_id = config.DATABASE_CHAT_ID
    decoded_data = url_safe.decode_data(encoded_data).split("-")
    if len(decoded_data) == 2:
        return [int(int(decoded_data[1]) / abs(database_chat_id))]

    elif len(decoded_data) == 3:
        start_id = int(int(decoded_data[1]) / abs(database_chat_id))
        end_id = int(int(decoded_data[2]) / abs(database_chat_id))

        if start_id < end_id:
            return range(start_id, end_id + 1)

        return range(start_id, end_id - 1, -1)


async def paste_content(content: str) -> Optional[str]:
    service_url = "https://paste.rs"

    async with ClientSession() as session:
        async with session.post(service_url, data=content) as response:
            if response.status != 201:
                return None

            raw_url = await response.text()
            return raw_url.strip()

    return None
