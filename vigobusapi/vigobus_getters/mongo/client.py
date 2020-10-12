"""CLIENT
Manage the MongoDB async connection
"""

# # Native # #
import asyncio

# # Installed # #
from motor import motor_asyncio
from pymongo import TEXT
from pymongo.collection import Collection

# # Project # #
from vigobusapi.settings import settings

__index_created = False


def get_collection(loop: asyncio.AbstractEventLoop) -> Collection:
    """Get the MongoDB Stops collection, using the given asyncio Loop"""
    global __index_created
    client = motor_asyncio.AsyncIOMotorClient(settings.mongo_uri, io_loop=loop)
    collection: Collection = client[settings.mongo_stops_db][settings.mongo_stops_collection]

    # Create a Text Index on stop name, for search
    # https://docs.mongodb.com/manual/core/index-text/#create-text-index
    if not __index_created:
        asyncio.ensure_future(collection.create_index([("name", TEXT)], background=True, default_language="spanish"))
        __index_created = True

    return collection
