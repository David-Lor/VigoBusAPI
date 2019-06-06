
# # Native # #
from typing import List, Union

# # Installed # #
from pybuses import Stop, Bus, StopNotExist, GetterResourceUnavailable
from bs4 import BeautifulSoup

# # Package # #
from .string_fixes import fix_bus


def parse_html(content: str, buses: bool) -> Union[Stop, List[Bus]]:
    """Parse the HTML content returned after requesting the HTML data source, and parse the Stop info and List of buses
    :param content: HTML source code as string
    :param buses: if True, parse the Buses
    :raises: pybuses.StopNotExist | pybuses.GetterResourceUnavailable
    """
    if "Parada Inexistente" in content:
        raise StopNotExist()

    html = BeautifulSoup(content, "html.parser")

    if not buses:
        # Parse Stop info
        stop_name = html.find("span", {"id": "lblNombre"}).text
        if not stop_name:
            raise GetterResourceUnavailable("Parsed Stop Name is empty")
        return Stop(
            stopid=0,  # TODO Parse stop id
            name=stop_name
        )

    else:
        # Parse Buses
        buses = list()
        rows_all = html.find("tr")
        rows = [
            r for r in rows_all
            if "style" in r.attrs.keys()
               and ("color:#333333;background-color:#F7F6F3;" in r.attrs["style"]
                    or "color:#284775;background-color:White;" in r.attrs["style"])
        ]
        for row in rows:
            # TODO add Try with possible exceptions based on wrong parse keys
            cols = row.find("td")
            line = cols[0].text.replace(" ", "")
            route = cols[1].text.lstrip()
            time = cols[2].text
            line, route = fix_bus(line, route)
            buses.append(Bus(
                line=line,
                route=route,
                time=int(time)
            ))
        return buses
