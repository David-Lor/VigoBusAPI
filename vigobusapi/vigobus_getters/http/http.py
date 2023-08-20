"""HTTP DATA SOURCE
Async functions to fetch data from the HTTP external data source and parse them to return the final objects.
"""

# # Project # #
from vigobusapi.services import http_request
from vigobusapi.entities import Stop, BusesResponse
from vigobusapi.logger import logger

# # Package # #
from .http_parser import parse_http_response_for_stop, parse_http_response_for_buses

__all__ = ("get_stop", "get_buses")

ENDPOINT_URL = "https://datos.vigo.org/vci_api_app/api2.jsp"


async def _request_stop(stop_id: int) -> dict:
    """Perform a request against the HTTP API. The endpoint returns both data for buses passing by and stop info,
    so it can be used for acquiring both information.
    Returns the response body as parsed dict (since the remote API returns a JSON payload)."""
    # TODO Cache HTTP API responses (in case a Stop and Buses are queried in short time)
    params = {"id": stop_id, "ttl": 5, "tipo": "TRANSPORTE-ESTIMACION-PARADA"}
    response = await http_request(
        url=ENDPOINT_URL,
        params=params
    )
    return response.json()


async def get_stop(stop_id: int) -> Stop:
    """Async function to get information of a Stop from the HTTP API data source.
    :param stop_id: Stop ID
    :raises: requests_async.Timeout | requests_async.RequestException |
             exceptions.StopNotExist | exceptions.exceptions.ParseError
    """
    logger.bind(**locals()).debug("Searching stop on external HTTP API data source...")

    response_json = await _request_stop(stop_id)
    stop_response = parse_http_response_for_stop(response_json)

    logger.bind(stop_response_data=stop_response.dict()).debug("Parsed Stop")
    return stop_response


async def get_buses(stop_id: int, get_all_buses: bool = False) -> BusesResponse:
    """Async function to get the buses incoming to a Stop from the HTTP API data source.
    The remote data source always returns the whole list of buses, but the output is shortened if get_all_buses=False.
    """
    logger.bind(**locals()).debug("Searching buses on external HTTP API data source...")

    response_json = await _request_stop(stop_id)
    buses_response = parse_http_response_for_buses(data=response_json,
                                                   get_all_buses=get_all_buses, verify_stop_exists=False)

    logger.bind(buses_response_data=buses_response.dict()).debug("Generated BusesResponse")
    return buses_response
