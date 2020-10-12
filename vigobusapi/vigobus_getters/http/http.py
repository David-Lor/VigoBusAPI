"""HTTP DATA SOURCE
Async functions to fetch data from the HTTP external data source and parse them to return the final objects.
"""

# # Project # #
from vigobusapi.support_services import http_request
from vigobusapi.entities import BusesResponse
from vigobusapi.settings import settings
from vigobusapi.logger import logger

# # Package # #
from .http_parser import parse_http_response

__all__ = ("get_buses",)

ENDPOINT_URL = "https://datos.vigo.org/vci_api_app/api2.jsp"


async def get_buses(stop_id: int, get_all_buses: bool = False) -> BusesResponse:
    """Async function to get the buses incoming to a Stop from the HTML data source.
    The remote data source always returns the whole list of buses, but the output is shortened if get_all_buses=False.
    """
    logger.debug("Searching buses on external HTTP data source...")

    params = {"id": stop_id, "ttl": 5, "tipo": "TRANSPORTE-ESTIMACION-PARADA"}
    response = await http_request(
        url=ENDPOINT_URL,
        params=params
    )

    buses_response = parse_http_response(data=response.json(), get_all_buses=get_all_buses, verify_stop_exists=False)
    logger.bind(buses_response_data=buses_response.dict()).debug("Generated BusesResponse")

    return buses_response
