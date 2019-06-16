"""AUTO GETTERS
Definition of getters that will run with the source='auto' (default).
Usually they will use a main data source and an extra data source as a backup
(e.g. the Stop getter will use the WSDL API as primary source; if it fails, it will try with the HTML data source)
"""

# # Native # #
import inspect
from typing import Optional

# # Installed # #
from pybuses_entities import Stop, BusesResult, StopNotExist

# # Package # #
from . import html, wsdl, cache

__all__ = ("get_stop", "get_buses")

STOP_GETTERS = (
    cache.get_stop,
    # TODO Local Storage getter
    wsdl.get_stop,
    html.get_stop
)
"""List of Stop Getter functions. 
The first function always is a local Cache storage. 
The second function always is a local Database storage."""

BUS_GETTERS = (
    cache.get_buses,
    html.get_buses
)
"""List of Bus Getter functions.
The first function always is a local Cache storage."""


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop, using the following getters in order:
    1.- Local Stops cache;
    2.- Local Stops database; (TODO)
    3.- Remote WSDL API data source
    4.- Remote
    :param stopid: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             pybuses_entities.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    last_exception = None

    for stop_getter in STOP_GETTERS:
        try:
            if inspect.iscoroutinefunction(stop_getter):
                stop: Stop = await stop_getter(stopid)
            else:
                stop: Stop = stop_getter(stopid)

        except StopNotExist as ex:
            last_exception = ex
            break

        except Exception as ex:
            last_exception = ex

        else:
            if stop is not None:
                if STOP_GETTERS.index(stop_getter) > 0:
                    # Save the Stop in cache if not found by the cache
                    cache.save_stop(stop)
                return stop

    # If Stop not returned, raise the Last Exception
    raise last_exception


async def get_buses(stopid: int, get_all_buses: bool) -> BusesResult:
    last_exception = None

    for bus_getter in BUS_GETTERS:
        try:
            if inspect.iscoroutinefunction(bus_getter):
                buses_result: Optional[BusesResult] = await bus_getter(stopid, get_all_buses)
            else:
                buses_result: Optional[BusesResult] = bus_getter(stopid, get_all_buses)

        except StopNotExist as ex:
            last_exception = ex
            break

        except Exception as ex:
            last_exception = ex

        else:
            if buses_result is not None:
                if BUS_GETTERS.index(bus_getter) > 0:
                    # Save the Buses in cache if bus list not found by the cache itself
                    cache.save_buses(stopid, get_all_buses, buses_result.buses)
                return buses_result

    # If Buses not returned, raise the Last Exception
    raise last_exception
