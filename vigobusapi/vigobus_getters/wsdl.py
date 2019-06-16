
# # Installed # #
from pybuses_entities import Stop, StopNotExist
from requests_async import HTTPError

# # Package # #
from .wsdl_request import request_wsdl_stop
from .wsdl_parser import parse_xml_stop, parse_xml_error_stop_not_exist


__all__ = ("get_stop",)


async def get_stop(stopid: int) -> Stop:
    """Async function to get information of a Stop (only name) from the WSDL API.
    :raises: requests_async.RequestTimeout | requests_async.RequestException | pybuses_entities.StopNotExist
    """
    try:
        xml = await request_wsdl_stop(stopid)

    except HTTPError as request_error:
        # When the Stop not exists, the WSDL API returns 500 causing a HTTPError
        # We use the following parser helper to check if the API returned an error because the stop not exists
        if parse_xml_error_stop_not_exist(request_error.response.text):
            raise StopNotExist()
        else:
            raise request_error

    else:
        return parse_xml_stop(xml)
