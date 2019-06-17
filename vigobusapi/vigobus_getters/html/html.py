"""HTML
Async functions to fetch data from the HTML external data source and parse them to return the final objects.
"""

# # Installed # #
from pybusent import Stop, BusSort, BusesResult
from requests_async import RequestException

# # Parent Package # #
from ..exceptions import ParsingExceptions

# # Package # #
from .html_request import request_html
from .html_parser import *

__all__ = ("get_stop", "get_buses")


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (only name) from the HTML data source.
    :param stopid: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             pybusent.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    return parse_stop(html_source)


async def get_buses(stopid: int, get_all_buses: bool = False) -> BusesResult:
    """Async function to get the buses incoming on a Stop from the HTML data source.
    Return the List of Buses AND True if more bus pages available, False if the current bus list was the only page.
    :param stopid: Stop ID
    :param get_all_buses: if True, get all Buses through all the HTML pages available
    :raises: requests_async.RequestTimeout | requests_async.RequestException |
             pybusent.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    html_source = await request_html(stopid)
    # stop = parse_stop(html_source)
    buses = parse_buses(html_source)
    current_page, pages_available = parse_pages(html_source)
    more_buses_available = bool(pages_available)

    # Try to parse extra pages available, if any
    if get_all_buses and more_buses_available:
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

        else:
            more_buses_available = False

        finally:
            clear_duplicated_buses(buses)

    return BusesResult(
        buses=sorted(buses, key=BusSort.time_line_route),
        more_buses_available=more_buses_available,
        # stop=stop
    )
