"""HTTP_PARSER
Parsers for the HTTP external data source

Sample of JSON payload returned by HTTP API:

{
   "estimaciones":[
      {
         "minutos":25,
         "metros":4126,
         "linea":"18",
         "ruta":"\"A\" SARDOMA por MANTELAS"
      },
      {
         "minutos":85,
         "metros":15120,
         "linea":"18",
         "ruta":"\"A\" SARDOMA por MANTELAS"
      }
   ],
   "parada":[
      {
         "nombre":"Baixada á Laxe  44",
         "latitud":42.216415126,
         "longitud":-8.719355076,
         "stop_vitrasa":2290
      }
   ]
}
"""

# # Project # #
from vigobusapi.entities import Stop, Bus, Buses, BusesResponse
from vigobusapi.vigobus_getters.string_fixes import fix_stop_name, fix_bus
from vigobusapi.vigobus_getters.helpers import sort_buses
from vigobusapi.exceptions import StopNotExist
from vigobusapi.settings import settings

__all__ = ("parse_http_response_for_stop", "parse_http_response_for_buses")


def parse_http_response_for_stop(data: dict) -> Stop:
    """Parse a HTTP API response and extract the Stop data from it.
    :param data: JSON payload returned by HTTP API
    :raises: exceptions.StopNotExist
    """
    stop_data = data["parada"][0]
    stop_id = stop_data["stop_vitrasa"]
    stop_original_name = stop_data["nombre"]
    stop_fixed_name = fix_stop_name(stop_original_name)
    stop_lat = stop_data.get("latitud")
    stop_lon = stop_data.get("longitud")

    return Stop(
        stop_id=stop_id,
        name=stop_fixed_name,
        original_name=stop_original_name,
        lat=stop_lat,
        lon=stop_lon
    )


def parse_http_response_for_buses(data: dict, get_all_buses: bool, verify_stop_exists: bool = True) -> BusesResponse:
    """Parse a HTTP API response and extract the Stop data from it.
    :param data: JSON payload returned by HTTP API
    :param get_all_buses: if True, limit parsed & returned list of buses to settings.buses_normal_limit
    :param verify_stop_exists: if the payload does not contain stop info, it will be considered that the stop
                               does not exist. In this case, if this argument is True, raise the StopNotExist exception
    :raises: exceptions.StopNotExist
    """
    if verify_stop_exists and not data["parada"]:
        raise StopNotExist()

    buses: Buses = list()
    more_buses_available = False

    for i, bus_raw in enumerate(data["estimaciones"], start=1):
        line = bus_raw["linea"]
        route = bus_raw["ruta"]
        time = bus_raw["minutos"]
        line, route = fix_bus(line=line, route=route)

        buses.append(Bus(
            line=line,
            route=route,
            time=time
        ))

    # TODO Try to save complete buses cache before limiting the response, so it can be reused later without re-request
    sort_buses(buses)
    if not get_all_buses and len(buses) > settings.buses_normal_limit:
        buses = buses[:settings.buses_normal_limit]
        more_buses_available = True

    return BusesResponse(
        buses=buses,
        more_buses_available=more_buses_available
    )
