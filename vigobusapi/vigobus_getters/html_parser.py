"""HTML_PARSER
Parsers for the HTML external data source.
"""

# # Native # #
from typing import List, Tuple, Dict
from copy import deepcopy

# # Installed # #
from pybuses import Stop, Bus, StopNotExist
from bs4 import BeautifulSoup

# # Package # #
from .html_const import *
from .string_fixes import fix_bus, fix_stop_name
from .exceptions import ParseError, ParsingExceptions

__all__ = ("parse_stop", "parse_buses", "parse_pages", "parse_extra_parameters", "assert_page_number")


def parse_stop(html_source: str) -> Stop:
    """Parse the HTML content returned after requesting the HTML data source,
    parsing parse the Stop info and returning a Stop object.
    :param html_source: HTML source code as string
    :raises: pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    parse_stop_exists(html_source)
    html = BeautifulSoup(html_source, HTML_PARSER)
    # TODO Pasar como parámetro el BeautifulSoup parsed en lugar de parsear en cada método

    try:
        stop_id = int(html.find("span", {"id": "lblParada"}).text)
        stop_name = html.find("span", {"id": "lblNombre"}).text
        if not stop_name:
            raise ParseError("Parsed Stop Name is empty")
        stop_name = fix_stop_name(stop_name)

        return Stop(
            stopid=stop_id,
            name=stop_name
        )

    except ParsingExceptions:
        raise ParseError()


def parse_buses(html_source: str) -> List[Bus]:
    """Parse the HTML content returned after requesting the HTML data source, and parse the Stop info and List of buses.
    :param html_source: HTML source code as string
    :return: List of buses
    :raises: pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    parse_stop_exists(html_source)
    buses = list()
    html = BeautifulSoup(html_source, HTML_PARSER)

    try:
        buses_table = html.find("table", {"id": "GridView1"})
        # If buses_table is not found, means no buses are available
        if buses_table:
            buses_rows = buses_table.find_all("tr")

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

                # TODO TOFIX Sometimes, Page numbers parsed as a bus!!!

        return buses

    except ParsingExceptions:
        raise ParseError()


def parse_stop_exists(html_source: str, raise_exception: bool = True) -> bool:
    """Given the HTML source code returned by HTTP request (str), detect if the stop was found or not.
    Must be called at the beggining of parse_stop/parse_buses helpers.
    If raise_exception is True, pybuses.StopNotExist is raised if the stop not exists.
    Otherwise, return True if the stop exists, return False if not exists.
    :param html_source: HTML source code
    :param raise_exception: if True, raise StopNotExist if the stop not exists (default=True)
    :return: True if stop exists; False if stop not exists (only if raise_exception=False)
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
    try:
        html = BeautifulSoup(html_source, HTML_PARSER)

        params = {key: None for key in EXTRA_DATA_REQUIRED}
        for key in params.keys():
            value = html.find("input", {"id": key})["value"]
            params[key] = value

        return params

    except ParsingExceptions:
        raise ParseError()


def parse_pages(html_source: str) -> Tuple[int, int]:
    """Parse the pages on the current page, returning the current page number, and how many pages
    are available after the current one.
    :param html_source: HTML source code
    :return: Current page number; Ammount of pages available after the current
    :raises: vigobus_getters.exceptions.ParseError
    """
    try:
        html = BeautifulSoup(html_source, HTML_PARSER)
        href_pages = set()  # Pages with <a> tag, meaning they are not the current number

        # Table that contains the page numbers
        numbers_table = html.find(**PARSER_PAGE_NUMBERS_TABLE)
        if numbers_table is None:  # No table found = no more pages available
            raise ZeroDivisionError()

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

    except ZeroDivisionError:
        # Raised this error when No pages available (return: current page = 1; additional pages available = 0)
        return 1, 0

    except ParsingExceptions:
        raise ParseError()


def assert_page_number(html_source: str, expected_current_page: int):
    """Parse the page number of the current page and assert (compare) with the expected page number.
    If numbers won't match, ParseError is raised.
    :param html_source: HTML source code
    :param expected_current_page: expected current page number
    :raises: vigobus_getters.exceptions.ParseError
    """
    try:
        current_page, pages_left = parse_pages(html_source)
        print("current page", current_page, "pages left", pages_left)
        assert current_page == expected_current_page
    except ParsingExceptions:
        raise ParseError()
