"""HTML
Async functions to fetch data from the HTML external data source and parse them to return the final objects.
"""

# # Native # #
import asyncio
from typing import List

# # Installed # #
from pybuses import Stop, Bus
from cachetools import TTLCache
from asyncache import cached
from requests_async import RequestException

# # Package # #
from .html_request import request_html
from .html_parser import *
from .exceptions import ParsingExceptions

__all__ = ("get_stop", "get_buses")

stops_cache = TTLCache(maxsize=1000, ttl=86400)
buses_cache = TTLCache(maxsize=500, ttl=15)


@cached(stops_cache)  # TODO exceptions are cached ?
async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (only name) from the HTML data source.
    :param stopid: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    return parse_stop(html_source)


@cached(buses_cache)  # TODO exceptions are cached ?
async def get_buses(stopid: int, get_all_pages: bool = False) -> List[Bus]:
    """Async function to get the buses incoming on a Stop from the HTML data source.
    :param stopid: Stop ID
    :param get_all_pages: if True, get all available Bus pages
    :raises: requests_async.RequestTimeout | requests_async.RequestException |
             pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    buses = parse_buses(html_source)

    # Try to parse extra pages available, if any
    if get_all_pages and buses:
        current_page, pages_available = parse_pages(html_source)

        if pages_available:
            # Get and Parse extra pages available
            extra_parameters = parse_extra_parameters(html_source)
            tasks = [  # async request_html() tasks (one request per page)
                request_html(stopid, page=current_page, extra_params=extra_parameters)
                for current_page in list(range(2, pages_available + 2))
            ]

            try:
                # execute all the requests async and wait for their responses
                tasks_results = await asyncio.gather(*tasks)
            except RequestException:
                # if the extra buses could not be fetched, ignore this error and return the first page of results
                pass
            else:
                try:
                    # parse the received responses
                    for current_page, html_source in enumerate(tasks_results, 2):
                        assert_page_number(html_source, current_page)
                        more_buses = parse_buses(html_source)
                        buses.extend(more_buses)
                except ParsingExceptions:
                    # if processing the extra buses give a Parsing exception, ignore this error
                    pass

    return buses
