"""HTML_PARSER
Parsers for the HTML external data source.
"""

# # Native # #
import contextlib
import urllib.parse
from collections import Counter
from typing import Tuple, Dict

# # Installed # #
from pybusent import Bus, Buses, StopNotExist
from bs4 import BeautifulSoup

# # Parent Package # #
from ..entities import Stop
from ..string_fixes import fix_bus, fix_stop_name
from ..exceptions import ParseError, ParsingExceptions

# # Package # #
from .html_const import *

__all__ = (
    "parse_stop", "parse_buses", "parse_pages", "parse_extra_parameters",
    "assert_page_number", "clear_duplicated_buses"
)


@contextlib.contextmanager
def parsing():
    """ContextManager to run code that parse HTML. If any of ParsingExceptions is raised inside the CM,
    ParseError is raised to the outside.
    """
    try:
        yield
    except ParsingExceptions as ex:
        raise ParseError(ex)


def parse_stop(html_source: str) -> Stop:
    """Parse the HTML content returned after requesting the HTML data source,
    parsing parse the Stop info and returning a Stop object.
    :param html_source: HTML source code as string
    :raises: pybusent.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    parse_stop_exists(html_source)
    html = BeautifulSoup(html_source, HTML_PARSER)
    # TODO BeautifulSoup-parsed object should be passed instead of raw HTML string

    with parsing():
        stop_id = int(html.find(**PARSER_STOP_ID).text)
        stop_name = html.find(**PARSER_STOP_NAME).text
        if not stop_name:
            raise ParseError("Parsed Stop Name is empty")
        stop_name = fix_stop_name(stop_name)

        return Stop(
            stopid=stop_id,
            name=stop_name
        )


def parse_buses(html_source: str) -> Buses:
    """Parse the HTML content returned after requesting the HTML data source, and parse the Stop info and List of buses.
    :param html_source: HTML source code as string
    :return: List of buses
    :raises: pybusent.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    parse_stop_exists(html_source)
    buses = list()
    html = BeautifulSoup(html_source, HTML_PARSER)

    with parsing():
        buses_table = html.find(**PARSER_BUSES_TABLE)
        # If buses_table is not found, means no buses are available
        if buses_table:
            buses_rows = list()
            for parser in PARSERS_BUSES_ROWS_INSIDE_TABLE:
                buses_rows.extend(buses_table.find_all(**parser))

            for row in buses_rows:
                bus_data_columns = row.find_all("td")

                if len(bus_data_columns) == 3:  # The header is a row but without <td>; <th> instead
                    line = bus_data_columns[0].text.replace(" ", "")
                    route = bus_data_columns[1].text.strip()
                    time = int(bus_data_columns[2].text)
                    line, route = fix_bus(line, route)
                    buses.append(Bus(
                        line=line,
                        route=route,
                        time=time
                    ))

        return buses


def parse_stop_exists(html_source: str, raise_exception: bool = True) -> bool:
    """Given the HTML source code returned by HTTP request (str), detect if the stop was found or not.
    Must be called at the beggining of parse_stop/parse_buses helpers.
    If raise_exception is True, pybusent.StopNotExist is raised if the stop not exists.
    Otherwise, return True if the stop exists, return False if not exists.
    :param html_source: HTML source code
    :param raise_exception: if True, raise StopNotExist if the stop not exists (default=True)
    :return: True if stop exists; False if stop not exists (only if raise_exception=False)
    :raises: pybusent.StopNotExist
    """
    exists = "Parada Inexistente" not in html_source
    if raise_exception and not exists:
        raise StopNotExist()
    else:
        return exists


def parse_extra_parameters(html_source: str) -> Dict:
    """Parse the Extra parameters (__VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION)
    required to fetch more pages, and return them as a Dict.
    :param html_source: HTML source code
    :return: Dict with the extra parameters
    :raises: vigobus_getters.exceptions.ParseError
    """
    with parsing():
        html = BeautifulSoup(html_source, HTML_PARSER)

        params = {key: None for key in EXTRA_DATA_REQUIRED}
        for key in params.keys():
            value = html.find("input", {"id": key})["value"]
            # Values must be URL-Parsed (e.g. replace '/' by '%2F' - https://www.urlencoder.io/python/)
            params[key] = urllib.parse.quote(value, safe="")

        return params


def parse_pages(html_source: str) -> Tuple[int, int]:
    """Parse the pages on the current page, returning the current page number, and how many pages
    are available after the current one.
    :param html_source: HTML source code
    :return: Current page number; Ammount of pages available after the current
    :raises: vigobus_getters.exceptions.ParseError
    """
    with parsing():
        html = BeautifulSoup(html_source, HTML_PARSER)
        href_pages = set()  # Pages with <a> tag, meaning they are not the current number

        # Table that contains the page numbers
        numbers_table = html.find(**PARSER_PAGE_NUMBERS_TABLE)

        # No table found = no more pages available
        if numbers_table is None:
            # return: current page = 1; additional pages available = 0)
            return 1, 0

        # Current page inside that table
        current_page = int(numbers_table.find(**PARSER_PAGE_NUMBER_CURRENT_INSIDE_TABLE).text)

        # All the linked numbers inside that table
        linked_pages_inside_table = numbers_table.find_all(**PARSER_PAGE_NUMBERS_LINKED_INSIDE_TABLE)

        # Parse all the valued found numbers
        for page_html in linked_pages_inside_table:
            try:
                page = int(page_html.text.strip())
                href_pages.add(page)
            except ValueError:
                pass

        # Get how many pages are left after the current page
        pages_left = sum(1 for n in href_pages if n > current_page)

        return current_page, pages_left


def assert_page_number(html_source: str, expected_current_page: int):
    """Parse the page number of the current page and assert (compare) with the expected page number.
    If numbers won't match, ParseError is raised.
    :param html_source: HTML source code
    :param expected_current_page: expected current page number
    :raises: vigobus_getters.exceptions.ParseError
    """
    with parsing():
        current_page, pages_left = parse_pages(html_source)
        assert current_page == expected_current_page, \
            f"Pages won't match. Current page is {current_page}, should be {expected_current_page}"


def clear_duplicated_buses(buses: Buses) -> Buses:
    """Given a List of Buses, find possible duplicated bus and remove them.
    Buses can be duplicated when getting all the pages from the HTML data source,
    and changes on the list of buses happen while fetching all the pages.
    If two (or more) buses have the same ID (same line & route) and a remaining time difference
    of 1 minute or less, they are considered duplicates.
    Duplicated bus/es are removed from the list in-place, so the same object is returned.
    """
    buses_ids = Counter()

    # Add IDs of found buses to the Counter dict
    for bus in buses:
        buses_ids[bus.busid] += 1

    # Remove not-duplicated Bus IDs from the Counter dict
    for bus_id in [bid for bid in buses_ids.keys() if buses_ids[bid] <= 1]:
        buses_ids.pop(bus_id)

    # Keep one of each duplicated buses depending on time
    buses_keep = list()
    for bus_id in buses_ids.keys():
        _buses = sorted(  # Buses with the same Bus ID, sorted by time
            [b for b in buses if b.busid == bus_id],
            key=lambda _bus: _bus.time
        )
        for bus in _buses:
            # Time range of bus.time +/- 1 minute
            time_range = [i for i in range(bus.time - 1, bus.time + 2)]
            # Search the already-kept buses with the same Bus ID in the time range
            n_repeated_buses = sum(  # 0 if no buses with a similar time are found
                1 for b in buses_keep
                if b.time in time_range
            )
            if not n_repeated_buses:
                # Keep the bus with the lowest time in the buses list
                buses_keep.append(bus)

    # Remove the repeated buses from the original buses list
    for bus in [b for b in buses if b.busid in buses_ids.keys()]:
        buses.remove(bus)

    # Add the kept buses to the original buses list
    buses.extend(buses_keep)
    return buses
