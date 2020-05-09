"""CLIENT
Manage the MongoDB async connection
"""

# # Installed # #
from motor import motor_asyncio
from pymongo.collection import Collection

# # Project # #
from vigobusapi.settings_handler import settings


def get_collection(loop) -> Collection:
    """Get the MongoDB Stops collection, using the given asyncio Loop"""
    # TODO how to initialize client only once?
    client = motor_asyncio.AsyncIOMotorClient(settings.mongo_uri, io_loop=loop)
    return client[settings.mongo_stops_db][settings.mongo_stops_collection]
