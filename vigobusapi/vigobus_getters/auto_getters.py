"""AUTO GETTERS
Functions called from request handlers to acquire data from local or external data sources,
depending on the availability.
"""

# # Native # #
import inspect
from typing import Optional, Callable

# # Project # #
from vigobusapi.vigobus_getters import html, cache, mongo
from vigobusapi.vigobus_getters.helpers import *
from vigobusapi.entities import *
from vigobusapi.exceptions import *
from vigobusapi.logger import logger

__all__ = ("get_stop", "get_buses")

STOP_GETTERS = (
    cache.get_stop,
    mongo.get_stop,
    html.get_stop
)
"""List of Stop Getter functions. 
The first function always is a local Cache storage. 
The second function always is a local Database storage.
Next functions are external data sources.
"""

BUS_GETTERS = (
    cache.get_buses,
    html.get_buses
)
"""List of Bus Getter functions.
The first function always is a local Cache storage.
Next functions are external data sources.
"""


async def get_stop(stop_id: int) -> Stop:
    """Async function to get information of a Stop, using the STOP_GETTERS in order
    :param stop_id: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             exceptions.StopNotExist | exceptions.ParseError
    """
    last_exception = None
    logger.debug(f"Getting stop {stop_id}")

    stop_getter: Callable
    for stop_getter in STOP_GETTERS:
        try:
            if inspect.iscoroutinefunction(stop_getter):
                stop: Stop = await stop_getter(stop_id)
            else:
                stop: StopOrNotExist = stop_getter(stop_id)

            if isinstance(stop, Exception):
                raise stop

        except StopNotExist as ex:
            last_exception = ex
            # Save the StopNotExist status in cache, if not found by the cache
            if STOP_GETTERS.index(stop_getter) > 0:
                cache.save_stop_not_exist(stop_id)
            break

        except Exception as ex:
            last_exception = ex

        else:
            if stop is not None:
                # Save the Stop on local data storages
                if STOP_GETTERS.index(stop_getter) > 0:
                    # Save the Stop in cache if not found by the cache
                    cache.save_stop(stop)
                if STOP_GETTERS.index(stop_getter) > 1:
                    # Save the Stop in MongoDB if not found by Mongo
                    add_stop_created_timestamp(stop)  # Add "created" field
                    await mongo.save_stop(stop)  # non-blocking

                # Add the Source to the returned data
                stop.source = get_package(stop_getter)

                return stop

    # If Stop not returned, raise the Last Exception
    raise last_exception


async def get_buses(stop_id: int, get_all_buses: bool) -> BusesResponse:
    """Async function to get information of a Stop, using the BUS_GETTERS in order
    :param stop_id: Stop ID
    :param get_all_buses: if True, fetch all the available buses
    :raises: requests_async.Timeout | requests_async.RequestException |
             exceptions.StopNotExist | exceptions.ParseError
    """
    last_exception = None

    # Lookup the Stop in cache; if available, verify that it exists
    cached_stop = cache.get_stop(stop_id)
    if isinstance(cached_stop, StopNotExist):
        raise cached_stop

    for bus_getter in BUS_GETTERS:
        try:
            if inspect.iscoroutinefunction(bus_getter):
                buses_result: Optional[BusesResponse] = await bus_getter(stop_id, get_all_buses)
            else:
                buses_result: Optional[BusesResponse] = bus_getter(stop_id, get_all_buses)

        except StopNotExist as ex:
            last_exception = ex
            break

        except Exception as ex:
            last_exception = ex

        else:
            if buses_result is not None:
                if BUS_GETTERS.index(bus_getter) > 0:
                    # Save the Buses in cache if bus list not found by the cache itself
                    cache.save_buses(stop_id, get_all_buses, buses_result)

                # Add the source to the returned data
                buses_result.source = get_package(bus_getter)

                return buses_result

    # If Buses not returned, raise the Last Exception
    raise last_exception
