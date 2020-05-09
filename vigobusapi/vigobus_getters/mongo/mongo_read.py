"""MONGO READ
Functions to async access and read Mongo data
"""

# # Native # #
import asyncio

# # Project # #
from vigobusapi.vigobus_getters.mongo.client import get_collection
from vigobusapi.entities import Stop, OptionalStop
from vigobusapi.logger import logger


async def read_stop(stop_id: int) -> OptionalStop:
    document = await get_collection(asyncio.get_event_loop()).find_one({"_id": stop_id})

    if document:
        logger.bind(mongo_read_document_data=document).debug("Read document from Mongo")
        return Stop(**document)
    else:
        logger.debug("No document found in Mongo")
