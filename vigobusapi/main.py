import fastapi
import uvicorn

from .routes import routes
from .settings import Settings

__all__ = ("VigoBusAPI",)


class VigoBusAPI:
    def __init__(self):
        self._settings = Settings.initialize()
        self._app = fastapi.FastAPI(
            title=self._settings.server.api.title,
            description=self._settings.server.api.description,
        )
        self._register_routes()

    def _register_routes(self):
        for router in routes:
            self._app.include_router(router)

    def run(self):
        uvicorn.run(
            app=self._app,
            host=self._settings.server.host,
            port=self._settings.server.port,
        )
