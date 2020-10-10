"""HTTP REQUESTER
Functions to perform HTTP requests
"""

# # Native # #
import time
from typing import *

# # Installed # #
from requests_async import request, Response, RequestException

# # Project # #
from vigobusapi.settings import settings
from vigobusapi.logger import logger

__all__ = ("http_request",)


async def http_request(
        url: str,
        method: str = "GET",
        params: Optional[dict] = None,
        body: Optional[Union[dict, str]] = None,
        headers: Optional[dict] = None,
        timeout: float = settings.http_timeout,
        retries: int = settings.http_retries,
        raise_for_status: bool = True,
        not_retry_400_errors: bool = True
) -> Response:
    """Async function to perform a generic HTTP request, supporting retries

    :param url: URL to request
    :param method: HTTP method (default=GET)
    :param params: URL query params as dict (default=None)
    :param body: request body, usually a dict or string (default=None)
    :param headers: request headers as dict (default=None)
    :param timeout: timeout for each request retry in seconds (default=from settings)
    :param retries: how many times to retry the request if it fails (default=from settings)
    :param raise_for_status: if True, raise HTTPError if response is not successful (default=True)
    :param not_retry_400_errors: if True, do not retry requests failed with a ~400 status code (default=True)
    :return: the Response object
    :raises: requests_async.RequestTimeout | requests_async.RequestException
    """
    last_error = None
    last_status_code = None

    for i in range(retries):
        with logger.contextualize(
            request_url=url,
            request_method=method,
            request_attemp=i+1,
            request_max_attempts=retries,
            request_params=params,
            request_body=body,
            request_headers=headers,
            request_timeout=timeout
        ):
            logger.debug("Requesting URL...")

            try:
                start_time = time.time()
                response: Response = await request(
                    method=method,
                    url=url,
                    params=params,
                    data=body,
                    headers=headers,
                    timeout=timeout
                )

                response_time = round(time.time() - start_time, 4)
                last_status_code = response.status_code
                logger.bind(
                    response_elapsed_time=response_time,
                    response_status_code=last_status_code,
                    response_body=response.text
                ).debug("Response received")

                if raise_for_status:
                    response.raise_for_status()
                return response

            except RequestException as ex:
                if not_retry_400_errors and last_status_code and 400 <= last_status_code < 500:
                    logger.warning("Request failed due to 400 error, not going to retry")
                    break

                logger.warning("Request failed")
                last_error = ex

    raise last_error
