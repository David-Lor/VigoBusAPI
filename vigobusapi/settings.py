import os
import pydantic

from vigobus.models.base import NEString, PosInt

ENV_FILE = os.getenv("ENV_FILE", None)
SETTINGS_FILE = os.getenv("SETTINGS_FILE", None)


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_FILE


class ServerSettings(pydantic.BaseSettings):

    class Api(pydantic.BaseSettings):
        title: NEString = "VigoBusAPI"
        description: str = ""

        class Config(BaseSettings.Config):
            env_prefix = "SERVER_API_"

    host: NEString = "0.0.0.0"
    port: PosInt = 5000
    api: Api = pydantic.Field(default_factory=Api)

    class Config(BaseSettings.Config):
        env_prefix = "SERVER_"


class Settings(pydantic.BaseModel):
    server: ServerSettings = pydantic.Field(default_factory=ServerSettings)

    @classmethod
    def initialize(cls) -> "Settings":
        # TODO Load from SETTINGS_FILE if given
        return cls()
