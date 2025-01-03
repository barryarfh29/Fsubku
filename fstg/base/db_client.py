import logging
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from fstg.utils import config

logger = logging.getLogger(__name__)


class Database:
    def __init__(self) -> None:
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[Any] = None

    async def connect(self) -> None:
        if not self.client:
            try:
                self.client = AsyncIOMotorClient(config.MONGODB_URL)
            except Exception as exception:
                logger.error(str(exception))
            else:
                self.db = self.client["FSUB_DATABASE"]["COLLECTIONS"]

    async def close(self) -> None:
        if self.client:
            self.client.close()

        self.client, self.db = None, None

    async def list_docs(self) -> List[str]:
        pipeline = [{"$project": {"_id": 1}}]
        cursor = self.db.aggregate(pipeline)
        return [document["_id"] async for document in cursor]

    async def get_doc(self, _id: int) -> Optional[Dict[str, Any]]:
        document = await self.db.find_one({"_id": _id})
        return document

    async def add_value(self, _id: int, key: str, value: Any) -> None:
        await self.db.update_one({"_id": _id}, {"$addToSet": {key: value}}, upsert=True)

    async def del_value(self, _id: int, key: str, value: Any) -> None:
        await self.db.update_one({"_id": _id}, {"$pull": {key: value}})

    async def clear_value(self, _id: int, key: str) -> None:
        await self.db.update_one({"_id": _id}, {"$unset": {key: ""}})

    async def del_doc(self, _id: int) -> None:
        await self.db.delete_one({"_id": _id})


database: Database = Database()
