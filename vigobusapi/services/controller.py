import fastapi

from vigobus import Vigobus
from vigobusapi.settings import Settings


class VigobusController:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._vigobus = Vigobus()

    async def get_stop_data(self, stop_id: int):
        return await self._vigobus.get_stop(stop_id)

    async def get_stop_buses(self, stop_id: int, get_all_buses: bool = False):
        return await self._vigobus.get_buses(stop_id, get_all_buses)

    @classmethod
    def get_from_request(cls, request: fastapi.Request):
        # import vigobusapi.main
        # app: vigobusapi.main.VigoBusAPI = request.app
        # return app.controller
        return request.app.controller
