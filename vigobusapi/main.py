import fastapi
import uvicorn

from vigobusapi.services.controller import VigobusController
from .routes import Routes
from .settings import Settings

__all__ = ("VigoBusAPI",)


class VigoBusAPI(fastapi.FastAPI):
    def __init__(self):
        self._settings = Settings.initialize()
        self._controller = VigobusController(self._settings)

        super().__init__(
            title=self._settings.server.api.title,
            description=self._settings.server.api.description,
        )
        self._register_routes()

    def _register_routes(self):
        routes = Routes.process_routes()
        if not routes:
            raise Exception("No registered API routes")

        for router in routes:
            self.include_router(router)

        self.openapi_tags = Routes.tags

    def run(self):
        uvicorn.run(
            app=self,
            host=self._settings.server.host,
            port=self._settings.server.port,
        )

    @property
    def controller(self):
        return self._controller
