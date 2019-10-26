"""MONGO READ
Functions to async access and read Mongo data
"""

# # Native # #
import asyncio

# # Package # #
from .client import get_collection

# # Project # #
from ...entities import Stop, OptionalStop


async def read_stop(stop_id: int) -> OptionalStop:
    document = await get_collection(asyncio.get_event_loop()).find_one({"_id": stop_id})
    if document:
        return Stop(**document)
