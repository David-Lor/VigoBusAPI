"""HTML
Async functions to fetch data from the HTML external data source and parse them to return the final objects.
"""

# # Native # #
from typing import List

# # Installed # #
from pybuses import Stop, Bus

# # Package # #
from .html_request import request_html
from .html_parser import parse_stop, parse_buses

__all__ = ("get_stop", "get_buses")


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (only name) from the HTML data source.
    :param stopid: Stop ID
    :raises: requests_async.RequestTimeout | requests_async.RequestException |
             pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html = await request_html(stopid)
    return parse_stop(html)


async def get_buses(stopid: int, get_all_pages: bool = False) -> List[Bus]:
    """Async function to get the buses incoming on a Stop from the HTML data source.
    :param stopid: Stop ID
    :param get_all_pages: if True, get all available Bus pages
    :raises: requests_async.RequestTimeout | requests_async.RequestException |
             pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html = await request_html(stopid)
    buses, pages = parse_buses(html)
    return buses
