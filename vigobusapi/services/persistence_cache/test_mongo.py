import contextlib

import pytest

from vigobus import Vigobus
from .mongo import MongoRepositoryCache
from ...settings import Settings


class MongoRepositoryCacheTest(MongoRepositoryCache):
    TEARDOWN = True

    @contextlib.asynccontextmanager
    async def test(self):
        try:
            yield self._mongo
        finally:
            await self.teardown()

    async def teardown(self):
        if self.TEARDOWN:
            self._collection_stops_data.delete_many(filter={})


@pytest.mark.asyncio
async def test_insert_stop_and_get():
    settings = Settings.initialize()
    mongo = MongoRepositoryCacheTest(settings.persistence)
    assert_exclude_fields = {"metadata"}
    # TODO Better assert metadata after deciding what to return from SourceMetadata

    async with mongo.test():
        vigobus = Vigobus()
        stop = await vigobus.get_stop(5800)

        await mongo.save_stop(stop)

        stop_read = await mongo.get_stop(stop.id)
        assert stop_read.dict(exclude=assert_exclude_fields) == stop.dict(exclude=assert_exclude_fields)
