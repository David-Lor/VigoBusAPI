"""HTML_PARSER
Parsers for the HTML external data source.
"""

# # Native # #
from typing import List, Tuple

# # Installed # #
from pybuses import Stop, Bus, StopNotExist
from bs4 import BeautifulSoup

# # Package # #
from .string_fixes import fix_bus, fix_stop_name
from .exceptions import ParseError, ParsingExceptions

__all__ = ("parse_stop", "parse_buses")


def parse_stop(html_source: str) -> Stop:
    """Parse the HTML content returned after requesting the HTML data source,
    parsing parse the Stop info and returning a Stop object.
    :param html_source: HTML source code as string
    :raises: pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    parse_stop_exists(html_source)
    html = BeautifulSoup(html_source, "html.parser")

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


def parse_buses(html_source: str) -> Tuple[List[Bus], int]:
    """Parse the HTML content returned after requesting the HTML data source, and parse the Stop info and List of buses.
    Return list of buses, number of pages available on the HTML data source (each page can show up to 5 buses).
    :param html_source: HTML source code as string
    :return: List of buses, Number of pages available on the data source
    :raises: pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    parse_stop_exists(html_source)
    buses = list()
    html = BeautifulSoup(html_source, "html.parser")

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

        return buses, 0

    except ParsingExceptions:
        raise ParseError()


def parse_stop_exists(html_source: str, raise_exception: bool = True) -> bool:
    """Given the HTML source code returned by HTTP request (str), detect if the stop was found or not.
    If raise_exception is True, pybuses.StopNotExist is raised if the stop not exists.
    Otherwise, return True if the stop exists, return False if not exists.
    """
    exists = "Parada Inexistente" not in html_source
    if raise_exception and not exists:
        raise StopNotExist()
    else:
        return exists
