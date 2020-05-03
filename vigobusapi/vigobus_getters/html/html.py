"""HTML
Async functions to fetch data from the HTML external data source and parse them to return the final objects.
"""

# # Installed # #
from requests_async import RequestException

# # Project # #
from vigobusapi.vigobus_getters.html.html_request import request_html
from vigobusapi.vigobus_getters.html.html_parser import *
from vigobusapi.vigobus_getters.exceptions import ParsingExceptions
from vigobusapi.entities import Stop, BusesResponse
from vigobusapi.logger import logger

__all__ = ("get_stop", "get_buses")


async def get_stop(stop_id: int) -> Stop:
    """Async function to get information of a Stop (only name) from the HTML data source.
    :param stop_id: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             exceptions.StopNotExist | exceptions.exceptions.ParseError
    """
    logger.debug("Searching stop on external HTML data source")
    html_source = await request_html(stop_id)
    return parse_stop(html_source)


async def get_buses(stop_id: int, get_all_buses: bool = False) -> BusesResponse:
    """Async function to get the buses incoming on a Stop from the HTML data source.
    Return the List of Buses AND True if more bus pages available, False if the current bus list was the only page.
    :param stop_id: Stop ID
    :param get_all_buses: if True, get all Buses through all the HTML pages available
    :raises: requests_async.RequestTimeout | requests_async.RequestException |
             exceptions.StopNotExist | exceptions.exceptions.ParseError
    """
    logger.debug("Searching buses on first page of external HTML data source")
    html_source = await request_html(stop_id)

    buses = parse_buses(html_source)
    _, pages_available = parse_pages(html_source)
    more_buses_available = bool(pages_available)

    logger.bind(
        buses=buses,
        pages_available=pages_available,
        more_buses_available=more_buses_available
    ).debug(f"Parsed {len(buses)} buses on the first page")

    # Try to parse extra pages available, if any
    if get_all_buses and more_buses_available:
        logger.debug("Searching for more buses on next pages")
        # Get and Parse extra pages available
        extra_parameters = parse_extra_parameters(html_source)

        try:
            for page in range(2, pages_available + 2):
                with logger.contextualize(current_page=page, pages_available=pages_available):
                    logger.debug(f"Searching buses on page {page}")
                    html_source = await request_html(stop_id, page=page, extra_params=extra_parameters)

                    assert_page_number(html_source, page)
                    more_buses = parse_buses(html_source)
                    logger.bind(buses=more_buses).debug(f"Parsed {len(more_buses)} buses on page {page}")

                    buses.extend(more_buses)

        except (RequestException, *ParsingExceptions):
            # Ignore exceptions while iterating the pages
            # Keep & return the buses that could be fetched
            logger.opt(exception=True).warning("Error while iterating pages")

        else:
            more_buses_available = False

    clear_duplicated_buses(buses)

    response = BusesResponse(
        buses=sorted(buses, key=lambda bus: (bus.time, bus.route)),
        more_buses_available=more_buses_available
    )
    logger.bind(buses_response_data=response.dict()).debug("Generated BusesResponse")
    return response
