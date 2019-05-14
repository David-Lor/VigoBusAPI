
# # Native # #
from typing import Dict, Optional
from os import getenv

# # Installed # #
# noinspection PyPackageRequirements
from dotenv import load_dotenv


def load_settings(dotenv_location: Optional[str] = None) -> Dict:
    if dotenv_location is None:
        dotenv_location = getenv("DOTENV_LOCATION")

    load_dotenv(dotenv_path=dotenv_location)

    return {
        "ENDPOINT_TIMEOUT": int(getenv("ENDPOINT_TIMEOUT", 100)),
        "HTTP_REQUEST_TIMEOUT": int(getenv("HTTP_REQUEST_TIMEOUT", 90)),
        "WSDL_REQUEST_TIMEOUT": int(getenv("WSDL_REQUEST_TIMEOUT", 90)),
        "API_STOP_TIMEOUT": int(getenv("API_STOP_TIMEOUT", 5)),
        "API_HOST": getenv("API_HOST", "0.0.0.0"),
        "API_PORT": int(getenv("API_PORT", 5000)),
        "API_NAME": getenv("API_NAME", "VigoBusAPI"),
        "HTTP_REMOTE_API": getenv("HTTP_REMOTE_API"),
        "WSDL_REMOTE_API": getenv("WSDL_REMOTE_API")
    }
