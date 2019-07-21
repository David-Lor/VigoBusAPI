"""MONGO READ
Functions to async access and read Mongo data
"""

# # Native # #
import asyncio

# # Package # #
from .client import get_collection

# # Parent Package # #
from ..entities import Stop, OptionalStop


async def read_stop(stopid: int) -> OptionalStop:
    # document = await stops_collection.find_one({"stopid": stopid})
    document = await get_collection(asyncio.get_event_loop()).find_one({"_id": stopid})
    if document:
        return Stop(**document)
