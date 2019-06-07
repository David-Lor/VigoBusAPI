"""SETTINGS
Settings loader. Load the DotEnv file and provide a function to return all the available settings as a Dict.
"""

# # Native # #
from typing import Dict, Optional
from os import getenv

# # Installed # #
# noinspection PyPackageRequirements
from dotenv import load_dotenv

# # Package # #
from .const import *


def load_settings(dotenv_location: Optional[str] = None) -> Dict:
    if dotenv_location is None:
        dotenv_location = getenv(DOTENV_LOCATION)

    load_dotenv(dotenv_path=dotenv_location)

    return {
        ENDPOINT_REQUEST_TIMEOUT: int(getenv(ENDPOINT_REQUEST_TIMEOUT, DEFAULT_ENDPOINT_REQUEST_TIMEOUT)),
        API_HOST: getenv(API_HOST, DEFAULT_API_HOST),
        API_PORT: int(getenv(API_PORT, DEFAULT_API_PORT)),
        API_NAME: getenv(API_NAME, DEFAULT_API_NAME),
        API_DESCRIPTION: getenv(API_DESCRIPTION),
        API_VERSION: getenv(API_VERSION, DEFAULT_API_VERSION),
        API_LOG_LEVEL: getenv(API_LOG_LEVEL, DEFAULT_API_LOG_LEVEL),
        HTTP_REMOTE_API: getenv(HTTP_REMOTE_API),
        WSDL_REMOTE_API: getenv(WSDL_REMOTE_API),
        HTTP_TIMEOUT: getenv(HTTP_TIMEOUT)
    }
