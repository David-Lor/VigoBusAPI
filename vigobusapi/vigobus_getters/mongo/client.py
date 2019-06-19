"""CLIENT
Manage the MongoDB async connection
"""

# # Installed # #
from motor import motor_asyncio
from pymongo.collection import Collection
# from pymongo.database import Database

# # Project # #
from vigobusapi.settings_handler import *

# __all__ = ("client", "stops_database", "stops_collection")
#
# settings = load_settings()
#
# client = motor_asyncio.AsyncIOMotorClient(settings[MONGO_URI])
# stops_database: Database = client[settings[MONGO_STOPS_DB]]
# stops_collection: Collection = stops_database[settings[MONGO_STOPS_COLLECTION]]

settings = load_settings()


def get_collection(loop) -> Collection:
    """Get the MongoDB Stops collection, using the given asyncio Loop"""
    client = motor_asyncio.AsyncIOMotorClient(settings[MONGO_URI], io_loop=loop)
    return client[settings[MONGO_STOPS_DB]][settings[MONGO_STOPS_COLLECTION]]
