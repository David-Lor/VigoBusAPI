"""MONGO READ
Functions to async write Mongo data
"""

# # Native # #
import asyncio

# # Installed # #
from pymongo.results import InsertManyResult

# # Package # #
from .client import get_collection

# # Parent Package # #
from ...entities import Stop

__all__ = ("insert_stops",)


async def insert_stops(*stops: Stop) -> InsertManyResult:
    """Insert one or multiple Stops in Mongo, provided as a single object or multiple args (comma separated).
    Return the Mongo Result on completion.
    """
    result = await get_collection(asyncio.get_event_loop()).insert_many([stop.get_mongo_dict() for stop in stops])
    return result
