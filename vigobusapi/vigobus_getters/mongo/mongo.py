"""MONGO
Async functions to fetch data from the MONGODB local data source and parse them to return the final objects.
"""

# # Native # #
import asyncio

# # Project # #
from vigobusapi.vigobus_getters.mongo.mongo_read import read_stop
from vigobusapi.vigobus_getters.mongo.mongo_write import insert_stops
from vigobusapi.entities import Stop, OptionalStop

__all__ = ("get_stop", "save_stop", "save_stops", "insert_stops")


async def get_stop(stop_id: int) -> OptionalStop:
    """Find a Stop previously saved on MongoDB and return it if available"""
    stop = await read_stop(stop_id)
    return stop


async def save_stops(*stops: Stop):
    """Save one or multiple Stops on MongoDB, provided as a single object or multiple args (comma separated).
    This function creates a fire & forget task on background, so other work can be done while the stop gets saved.
    Use the 'insert_stops' function to await for the stop/s to get saved and obtain the insertion result.
    """
    try:
        asyncio.create_task(insert_stops(*stops))
    except AttributeError:
        asyncio.ensure_future(insert_stops(*stops))


save_stop = save_stops
