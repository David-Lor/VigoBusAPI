"""HTML_PARSER
Parsers for the HTML external data source.
"""

# # Native # #
from typing import List, Union

# # Installed # #
from pybuses import Stop, Bus, StopNotExist
from bs4 import BeautifulSoup

# # Package # #
from .string_fixes import fix_bus
from .exceptions import ParseError, ParsingExceptions

__all__ = ("parse_html",)


def parse_html(content: str, buses: bool) -> Union[Stop, List[Bus]]:
    """Parse the HTML content returned after requesting the HTML data source, and parse the Stop info and List of buses
    :param content: HTML source code as string
    :param buses: if True, parse the Buses
    :raises: pybuses.StopNotExist | vigobus_getters.exceptions.ParseError
    """
    try:
        if "Parada Inexistente" in content:
            raise StopNotExist()

        html = BeautifulSoup(content, "html.parser")

        if not buses:
            # Parse Stop info
            stop_id = int(html.find("span", {"id": "lblParada"}).text)
            stop_name = html.find("span", {"id": "lblNombre"}).text
            if not stop_name:
                raise ParseError("Parsed Stop Name is empty")
            return Stop(
                stopid=stop_id,
                name=stop_name
            )

        else:
            # Parse Buses
            buses = list()
            buses_table = html.find("table", {"id": "GridView1"})
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

            return buses

    except ParsingExceptions:
        raise ParseError()
