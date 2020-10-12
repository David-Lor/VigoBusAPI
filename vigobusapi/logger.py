"""LOGGER
Logger instance
"""

# # Native # #
import sys

# # Installed # #
from loguru import logger

# # Project # #
from vigobusapi.settings import settings

__all__ = ("logger",)

LoggerFormat = "<green>{time:YY-MM-DD HH:mm:ss}</green> | " \
               "<level>{level}</level> | " \
               "{function}: <level>{message}</level> | " \
               "{extra} {exception}"

# Set custom logger
logger.remove()
logger.add(sys.stderr, level=settings.log_level.upper(), format=LoggerFormat)
