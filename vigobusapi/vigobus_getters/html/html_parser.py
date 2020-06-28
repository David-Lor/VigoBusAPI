"""HTML_PARSER
Parsers for the HTML external data source.
"""

# # Native # #
import contextlib
import urllib.parse
from collections import Counter
from typing import Tuple, Dict

# # Installed # #
from bs4 import BeautifulSoup

# # Project # #
from vigobusapi.vigobus_getters.html.html_const import *
from vigobusapi.vigobus_getters.string_fixes import fix_bus, fix_stop_name
from vigobusapi.vigobus_getters.exceptions import ParseError, ParsingExceptions
from vigobusapi.entities import Stop, Bus, Buses
from vigobusapi.exceptions import StopNotExist
from vigobusapi.logger import logger

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
    :raises: exceptions.StopNotExist | exceptions.exceptions.ParseError
    """
    parse_stop_exists(html_source)
    html = BeautifulSoup(html_source, HTML_PARSER)
    # TODO BeautifulSoup-parsed object should be passed instead of raw HTML string

    with parsing():
        stop_id = int(html.find(**PARSER_STOP_ID).text)
        stop_original_name = html.find(**PARSER_STOP_NAME).text
        if not stop_original_name:
            raise ParseError("Parsed Stop Name is empty")
        stop_name = fix_stop_name(stop_original_name)

        stop = Stop(
            stop_id=stop_id,
            name=stop_name,
            original_name=stop_original_name
        )
        logger.bind(stop_data=stop.dict()).debug("Parsed stop")
        return stop


def parse_buses(html_source: str) -> Buses:
    """Parse the HTML content returned after requesting the HTML data source, and parse the Stop info and List of buses.
    :param html_source: HTML source code as string
    :return: List of buses
    :raises: exceptions.StopNotExist | exceptions.exceptions.ParseError
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

        logger.bind(buses=buses).debug(f"Parsed {len(buses)} buses")
        return buses


def parse_stop_exists(html_source: str, raise_exception: bool = True) -> bool:
    """Given the HTML source code returned by HTTP request (str), detect if the stop was found or not.
    Must be called at the beggining of parse_stop/parse_buses helpers.
    If raise_exception is True, exceptions.StopNotExist is raised if the stop not exists.
    Otherwise, return True if the stop exists, return False if not exists.
    :param html_source: HTML source code
    :param raise_exception: if True, raise StopNotExist if the stop not exists (default=True)
    :return: True if stop exists; False if stop not exists (only if raise_exception=False)
    :raises: exceptions.StopNotExist
    """
    exists = "Parada Inexistente" not in html_source

    if not exists:
        logger.debug("The stop does not exist")
        if raise_exception:
            raise StopNotExist()

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

        logger.bind(extra_parameters=params).debug("Parsed extra parameters")
        return params


def parse_pages(html_source: str) -> Tuple[int, int]:
    """Parse the pages on the current page, returning the current page number, and how many pages
    are available after the current one.
    :param html_source: HTML source code
    :return: [Current page number, Ammount of pages available after the current]
    :raises: vigobus_getters.exceptions.ParseError
    """
    with parsing():
        html = BeautifulSoup(html_source, HTML_PARSER)
        href_pages = set()  # Pages with <a> tag, meaning they are not the current number

        # Table that contains the page numbers
        numbers_table = html.find(**PARSER_PAGE_NUMBERS_TABLE)

        # No table found = no more pages available
        if numbers_table is None:
            logger.debug("No extra pages found")
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

        logger.debug(f"Current page is {current_page}, with {pages_left} additional pages")
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
            f"Pages do not match. Current page is {current_page}, should be {expected_current_page}"


def clear_duplicated_buses(buses: Buses) -> Buses:
    """Given a List of Buses, find possible duplicated bus and remove them.
    Buses can be duplicated when getting all the pages from the HTML data source,
    as changes on the list of buses can happen while fetching all the pages.

    If two (or more) buses have the same bus_id (same line-route) and same time, they are considered duplicates.
    Still there is a small change of having two duplicated buses, with a diff of +/- 1min, since the time can change
    between pages requested. However this is ignored by now, to reduce code complexity.

    Duplicated bus/es are removed from the list in-place, so the same object is returned.
    """
    with logger.contextualize(buses=buses):
        buses_start = len(buses)
        buses_ids_times = Counter()
        """Counter with tuples (bus_id, time)"""
        for bus in buses:
            buses_ids_times[(bus.bus_id, bus.time)] += 1

        for bus_id, time in [tup for tup, count in buses_ids_times.items() if count > 1]:
            for i, repeated_bus in enumerate([bus for bus in buses if bus.bus_id == bus_id and bus.time == time]):
                if i > 0:
                    buses.remove(repeated_bus)

        buses_diff = buses_start - len(buses)
        logger.bind(buses_diff=buses_diff).debug(f"Cleared {buses_diff} duplicated buses")

        return buses
