"""MONGO READ
Functions to async access and read Mongo data
"""

# # Native # #
import asyncio
from typing import Optional

# # Installed # #
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCursor

# # Project # #
from vigobusapi.vigobus_getters.mongo.client import get_collection
from vigobusapi.entities import Stop, Stops, OptionalStop
from vigobusapi.logger import logger


async def read_stop(stop_id: int) -> OptionalStop:
    document = await get_collection(asyncio.get_event_loop()).find_one({"_id": stop_id})

    if document:
        logger.bind(mongo_read_document_data=document).debug("Read document from Mongo")
        return Stop(**document)
    else:
        logger.debug("No document found in Mongo")


async def search_stops(stop_name: str, limit: Optional[int] = None) -> Stops:
    documents = list()
    cursor: AsyncIOMotorCursor = get_collection(asyncio.get_event_loop()).find({
        "$text": {
            "$search": stop_name
        }
    })

    if limit is not None:
        cursor = cursor.limit(limit)

    async for document in cursor:
        documents.append(document)

    logger.bind(mongo_read_documents_data=documents).debug(f"Search in Mongo returned {len(documents)} documents")
    return [Stop(**document) for document in documents]
