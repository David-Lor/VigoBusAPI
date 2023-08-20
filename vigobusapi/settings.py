"""SETTINGS
Declaration of the Settings class and instance that can be used to get any setting required
"""

# # Native # #
import os
from typing import Optional

# # Installed # #
import pydantic
import pytimeparse

__all__ = ("settings", "google_maps_settings")

# TODO Split Settings by sections/groups in multiple classes

ENV_FILE = os.getenv("ENV_FILE", ".env")


class _BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_FILE


class Settings(_BaseSettings):
    endpoint_timeout: float = 30
    http_timeout: float = 5
    http_retries: int = 2
    stops_cache_maxsize: int = 500
    stops_cache_ttl: float = 3600
    buses_cache_maxsize: int = 300
    buses_cache_ttl: float = 15
    buses_normal_limit: int = 5
    buses_pages_async: bool = True
    mongo_uri = "mongodb://localhost:27017"
    mongo_stops_db = "vigobusapi"
    mongo_stops_collection = "stops"
    mongo_cache_maps_collection = "cache_maps"
    mongo_cache_maps_ttl: int = "60 days"  # seconds (can give human-readable time length, that will be converted)
    api_host = "0.0.0.0"
    api_port: int = 5000
    api_name = "VigoBusAPI"
    api_log_level = "info"
    log_level = "info"

    @pydantic.validator("mongo_cache_maps_ttl", pre=True)
    def _parse_duration(cls, v):
        """If the field is a non-digit string, parse a time length into seconds.
        The value must be defined with the values accepted by the parsing library:
        https://pypi.org/project/pytimeparse/"""
        if isinstance(v, str) and not v.isdigit():
            parsed_v = pytimeparse.parse(v)
            if parsed_v is None:
                raise ValueError(f"Invalid duration string \"{v}\"")
            return parsed_v
        return v


class GoogleMapsSettings(_BaseSettings):
    api_key: Optional[str] = None
    stop_map_default_size_x: int = 1280
    stop_map_default_size_y: int = 720
    stop_map_default_zoom: int = 17
    stop_map_default_type: str = "roadmap"  # TODO use enum (after refactoring to avoid circular dependency issue)
    stop_photo_default_size_x: int = 2000
    stop_photo_default_size_y: int = 2000
    language: str = "es"

    @property
    def enabled(self):
        return bool(self.api_key)

    class Config(_BaseSettings.Config):
        env_prefix = "GOOGLE_MAPS_"


settings = Settings()
google_maps_settings = GoogleMapsSettings()
