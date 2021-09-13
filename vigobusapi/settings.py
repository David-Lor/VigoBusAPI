"""SETTINGS
Declaration of the Settings class and instance that can be used to get any setting required
"""

# # Native # #
import os
from typing import Optional

# # Installed # #
import pydantic

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
    api_host = "0.0.0.0"
    api_port: int = 5000
    api_name = "VigoBusAPI"
    api_log_level = "info"
    log_level = "info"


class GoogleMapsSettings(_BaseSettings):
    api_key: Optional[str] = None
    stop_map_default_size_x: int = 1280
    stop_map_default_size_y: int = 720
    stop_map_default_zoom: int = 17
    stop_map_default_type: str = "roadmap"  # TODO use enum (after refactoring to avoid circular dependency issue)
    language: str = "es"

    @property
    def enabled(self):
        return bool(self.api_key)

    class Config(_BaseSettings.Config):
        env_prefix = "GOOGLE_MAPS_"


settings = Settings()
google_maps_settings = GoogleMapsSettings()
