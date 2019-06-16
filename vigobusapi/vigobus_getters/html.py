"""HTML
Async functions to fetch data from the HTML external data source and parse them to return the final objects.
"""

# # Native # #
from typing import Tuple

# # Installed # #
from pybuses_entities import Stop, BusSort, Buses
from requests_async import RequestException

# # Package # #
from .html_request import request_html
from .html_parser import *
from .exceptions import ParsingExceptions

__all__ = ("get_stop", "get_buses")


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (only name) from the HTML data source.
    :param stopid: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             pybuses_entities.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    return parse_stop(html_source)


async def get_buses(stopid: int, get_all_buses: bool = False) -> Tuple[Buses, bool]:
    """Async function to get the buses incoming on a Stop from the HTML data source.
    Return the List of Buses AND True if more bus pages available, False if the current bus list was the only page.
    :param stopid: Stop ID
    :param get_all_buses: if True, get all Buses through all the HTML pages available
    :return: List of Buses; True/False
    :raises: requests_async.RequestTimeout | requests_async.RequestException |
             pybuses_entities.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    buses = parse_buses(html_source)
    current_page, pages_available = parse_pages(html_source)

    # Try to parse extra pages available, if any
    if get_all_buses and pages_available:
        # Get and Parse extra pages available
        extra_parameters = parse_extra_parameters(html_source)

        try:
            for page in range(2, pages_available + 2):
                html_source = await request_html(stopid, page=page, extra_params=extra_parameters)
                assert_page_number(html_source, page)
                more_buses = parse_buses(html_source)
                # extra_parameters = parse_extra_parameters(html_source)  # Update extra_parameters
                buses.extend(more_buses)

        except (RequestException, *ParsingExceptions):
            # Ignore exceptions while iterating the pages; Keep & return the buses that could be fetched
            pass

        finally:
            clear_duplicated_buses(buses)

    return sorted(buses, key=BusSort.time_line_route), bool(pages_available)
