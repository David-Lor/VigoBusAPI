from typing import Optional

import motor.motor_asyncio
import pymongo.collection

import vigobus.models

from .base import BaseRepositoryCache
from ...settings import PersistenceSettings


class MongoRepositoryCache(BaseRepositoryCache):

    def __init__(self, settings: PersistenceSettings):
        self._settings = settings.mongodb
        self._mongo = motor.motor_asyncio.AsyncIOMotorClient(
            self._settings.uri,
            serverSelectionTimeoutMS=self._settings.connect_timeout_seconds * 1000,
        )
        self._database = self._mongo[self._settings.database]
        self._collection_stops_data: pymongo.collection.Collection = self._database[self._settings.collections.stops_data]

    async def get_stop(self, stop_id: int) -> Optional[vigobus.models.Stop]:
        document = await self._collection_stops_data.find_one(filter=self.get_filter_id(stop_id))
        if not document:
            return None

        stop = vigobus.models.Stop(
            id=document["_id"],
            **document,
        )
        return stop

    async def save_stop(self, stop: vigobus.models.Stop):
        document = {
            "_id": stop.id,
            **stop.dict(exclude={"id"}),
        }
        # noinspection PyUnresolvedReferences
        await self._collection_stops_data.insert_one(document)

    @classmethod
    def get_filter_id(cls, _id) -> dict:
        return {"_id": _id}
