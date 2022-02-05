"""MONGO READ
Functions to async access and read Mongo data
"""

# # Native # #
from typing import Optional

# # Installed # #
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCursor

# # Project # #
from vigobusapi.services import MongoDB
from vigobusapi.entities import Stop, Stops, OptionalStop
from vigobusapi.logger import logger


async def read_stop(stop_id: int) -> OptionalStop:
    document = await MongoDB.get_mongo().get_stops_collection().find_one({"_id": stop_id})

    if document:
        logger.bind(mongo_read_document_data=document).debug("Read document from Mongo")
        return Stop(**document)
    else:
        logger.debug("No document found in Mongo")


async def search_stops(stop_name: str, limit: Optional[int] = None) -> Stops:
    documents = list()
    cursor: AsyncIOMotorCursor = MongoDB.get_mongo().get_stops_collection().find({
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
