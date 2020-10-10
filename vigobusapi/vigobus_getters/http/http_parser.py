"""HTTP_PARSER
Parsers for the HTTP external data source
"""

# # Project # #
from vigobusapi.entities import Bus, Buses, BusesResponse
from vigobusapi.vigobus_getters.string_fixes import fix_bus
from vigobusapi.vigobus_getters.helpers import sort_buses
from vigobusapi.exceptions import StopNotExist
from vigobusapi.settings_handler import settings

__all__ = ("parse_http_response",)


def parse_http_response(data: dict, get_all_buses: bool, verify_stop_exists: bool = True) -> BusesResponse:
    if verify_stop_exists and not data["parada"]:
        raise StopNotExist()

    buses: Buses = list()
    more_buses_available = False

    for i, bus_raw in enumerate(data["estimaciones"], start=1):
        if not get_all_buses and i > settings.buses_normal_limit:
            more_buses_available = True
            break

        line = bus_raw["linea"]
        route = bus_raw["ruta"]
        time = bus_raw["minutos"]
        line, route = fix_bus(line=line, route=route)

        buses.append(Bus(
            line=line,
            route=route,
            time=time
        ))

    sort_buses(buses)
    return BusesResponse(
        buses=buses,
        more_buses_available=more_buses_available
    )
