from typing import Optional, List

import pydantic

from .base import BaseDatasource, Datasources
from ..exceptions import StopNotExistException
from ..models import BusesResponse, Bus, Stop, StopMetadata, BusMetadata
from ..models.base import NonNegInt, PosInt, Position, SourceMetadata
from ..utils import Utils


@Datasources.register(priority=1000)
class DatasourceVigoApi(BaseDatasource):
    _endpoint = "https://datos.vigo.org/vci_api_app/api2.jsp"

    class VigoAPIStopBusesResponse(pydantic.BaseModel):

        class InnerStop(pydantic.BaseModel):
            stop_vitrasa: PosInt
            nombre: str
            latitud: float
            longitud: float

        class InnerBus(pydantic.BaseModel):
            linea: str
            ruta: str
            minutos: NonNegInt
            metros: NonNegInt

        parada: List[InnerStop]  # Array of objects, always with 1 element, or empty if stop not exist.
        estimaciones: List[InnerBus]  # Array of objects, may be empty if no buses currently available.

        @property
        def stop(self) -> Optional[InnerStop]:
            if self.parada:
                return self.parada[0]
            return None

        @property
        def buses(self) -> List[InnerBus]:
            return self.estimaciones

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        response = await self._request_get_stop_buses(stop_id=stop_id)
        if not response.stop:
            raise StopNotExistException(stop_id=stop_id)

        buses = self._parse_response_buses(response)
        more_buses_available = False
        if not get_all_buses and self.buses_per_page:
            more_buses_available = len(buses) > self.buses_per_page
            buses = buses[:self.buses_per_page]

        return BusesResponse(
            buses=buses,
            more_buses_available=more_buses_available,
        )

    async def get_stop(self, stop_id: int) -> Optional[Stop]:
        response = await self._request_get_stop_buses(stop_id=stop_id)
        response_stop = response.stop
        if not response_stop:
            return None

        # noinspection PyTypeChecker
        return Stop(
            id=response_stop.stop_vitrasa,
            name=response_stop.nombre,
            position=Position(
                lat=response_stop.latitud,
                lon=response_stop.longitud,
            ),
            metadata=StopMetadata(
                original_name=response_stop.nombre,
                source=SourceMetadata(
                    datasource=self._class_name,
                    when=Utils.datetime_now(),
                ),
            ),
        )

    async def _request_get_stop_buses(self, stop_id: int) -> VigoAPIStopBusesResponse:
        params = {
            "id": stop_id,
            "ttl": 5,
            "tipo": "TRANSPORTE-ESTIMACION-PARADA",
        }

        r = await self._request_http(
            url=self._endpoint,
            params=params,
            raise_status=True,
        )
        return self.VigoAPIStopBusesResponse.parse_obj(r.json())

    def _parse_response_buses(self, response: VigoAPIStopBusesResponse) -> List[Bus]:
        now = Utils.datetime_now()

        # noinspection PyTypeChecker
        return [
            Bus(
                line=bus_received.linea,
                route=bus_received.ruta,
                time_minutes=bus_received.minutos,
                distance_meters=bus_received.metros,
                metadata=BusMetadata(
                    original_line=bus_received.linea,
                    original_route=bus_received.ruta,
                    source=SourceMetadata(
                        datasource=self._class_name,
                        when=now,
                    ),
                ),
            )
            for bus_received in response.estimaciones
        ]
