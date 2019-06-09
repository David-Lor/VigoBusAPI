"""HTML
Async functions to fetch data from the HTML external data source and parse them to return the final objects.
"""

# # Native # #
from typing import List

# # Installed # #
from pybuses import Stop, Bus
from requests_async import RequestException

# # Package # #
from .html_request import request_html
from .exceptions import ParseError
from .html_parser import *

__all__ = ("get_stop", "get_buses")


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (only name) from the HTML data source.
    :param stopid: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    return parse_stop(html_source)


async def get_buses(stopid: int, get_all_pages: bool = False) -> List[Bus]:
    """Async function to get the buses incoming on a Stop from the HTML data source.
    :param stopid: Stop ID
    :param get_all_pages: if True, get all available Bus pages
    :raises: requests_async.RequestTimeout | requests_async.RequestException |
             pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    buses = parse_buses(html_source)

    # Parse extra pages available
    if get_all_pages and buses:
        cp, pages_available = parse_pages(html_source)

        if pages_available:
            extra_parameters = parse_extra_parameters(html_source)

            for current_page in range(2, pages_available + 2):
                try:
                    html_source = await request_html(stopid, page=current_page, extra_params=extra_parameters)
                    assert_page_number(html_source, current_page)
                    more_buses = parse_buses(html_source)
                    # TODO check buses? if not repeated ?)
                    buses.extend(more_buses)
                except (ParseError, RequestException):
                    break

    return buses
