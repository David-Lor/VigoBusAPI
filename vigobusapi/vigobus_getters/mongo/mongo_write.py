"""MONGO READ
Functions to async write Mongo data
"""

# # Native # #
import asyncio

# # Installed # #
from pymongo.results import InsertManyResult

# # Project # #
from vigobusapi.vigobus_getters.mongo.client import get_collection
from vigobusapi.entities import Stop
from vigobusapi.logger import logger

__all__ = ("insert_stops",)


async def insert_stops(*stops: Stop, catch_errors: bool = False) -> InsertManyResult:
    """Insert one or multiple Stops in Mongo, provided as a single object or multiple args (comma separated).
    Return the Mongo Result on completion.
    :param catch_errors: if True, log errors and avoid raising them (useful when called as async background task)
    """
    try:
        insert_data = [stop.get_mongo_dict() for stop in stops]

        with logger.contextualize(mongo_insert_data=insert_data):
            logger.debug("Inserting stops in Mongo")
            result: InsertManyResult = await get_collection(asyncio.get_event_loop()).insert_many(insert_data)

            logger.bind(mongo_inserted_ids=result.inserted_ids).debug("Inserted stops in Mongo")
            return result

    except Exception as ex:
        if not catch_errors:
            raise ex
        logger.opt(exception=True).bind(stops=stops).error("Error while saving stop/s in MongoDB")
