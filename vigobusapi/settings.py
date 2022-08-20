import os
from typing import Optional

import pydantic

from vigobus.models.base import NEString, PosInt

ENV_FILE = os.getenv("ENV_FILE", None)
SETTINGS_FILE = os.getenv("SETTINGS_FILE", None)


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_FILE


class PersistenceSettings(pydantic.BaseModel):

    class MongoDB(pydantic.BaseSettings):

        class Collections(pydantic.BaseSettings):
            stops_data: str = "stops_data"

            class Config(BaseSettings.Config):
                env_prefix = "VGA_PERSISTENCE_MONGODB_COLLECTION_"

        uri: Optional[pydantic.AnyUrl] = None
        database: str = "vigobus"
        collections: Collections = pydantic.Field(default_factory=Collections)
        connect_timeout_seconds: float = 5

        class Config(BaseSettings.Config):
            env_prefix = "VGA_PERSISTENCE_MONGODB_"

    class Git(pydantic.BaseSettings):

        class Config(BaseSettings.Config):
            env_prefix = "VGA_PERSISTENCE_GIT_"

    mongodb: MongoDB = pydantic.Field(default_factory=MongoDB)
    git: Git = pydantic.Field(default_factory=Git)


class ServerSettings(pydantic.BaseSettings):

    class Api(pydantic.BaseSettings):
        title: NEString = "VigoBusAPI"
        description: str = ""

        class Config(BaseSettings.Config):
            env_prefix = "VGA_SERVER_API_"

    host: NEString = "0.0.0.0"
    port: PosInt = 5000
    api: Api = pydantic.Field(default_factory=Api)

    class Config(BaseSettings.Config):
        env_prefix = "VGA_SERVER_"


class Settings(pydantic.BaseModel):

    server: ServerSettings = pydantic.Field(default_factory=ServerSettings)
    persistence: PersistenceSettings = pydantic.Field(default_factory=PersistenceSettings)

    @classmethod
    def initialize(cls) -> "Settings":
        # TODO Load from SETTINGS_FILE if given
        return cls()
