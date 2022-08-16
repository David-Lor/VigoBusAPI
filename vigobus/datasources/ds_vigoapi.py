from typing import List

import pydantic

from .base import BaseDatasource, Datasources
from ..models import BusesResponse, Bus
from ..models.base import NonNegInt


@Datasources.register(priority=1000)
class DatasourceVigoAPI(BaseDatasource):
    _endpoint = "https://datos.vigo.org/vci_api_app/api2.jsp"

    class VigoAPIBusesResponse(pydantic.BaseModel):

        # class InnerStop(pydantic.BaseModel):
        #     latitud: float
        #     longitud: float
        #     stop_vitrasa: PosInt
        #     nombre: str

        class InnerBus(pydantic.BaseModel):
            linea: str
            ruta: str
            minutos: NonNegInt
            metros: NonNegInt

        # parada: InnerStop
        estimaciones: List[InnerBus]

    async def get_buses(self, stop_id: int, get_all_buses: bool = True) -> BusesResponse:
        params = {
            "id": stop_id,
            "ttl": 5,
            "tipo": "TRANSPORTE-ESTIMACION-PARADA",
        }

        r = await self._request_http(
            url=self._endpoint,
            params=params,
        )

        buses = self._parse_response_buses(r.json())
        more_buses_available = False
        if not get_all_buses and self.buses_per_page:
            buses = buses[:self.buses_per_page]
            more_buses_available = True

        return BusesResponse(
            buses=buses,
            more_buses_available=more_buses_available,
        )

    def _parse_response_buses(self, body: dict) -> List[Bus]:
        parsed = self.VigoAPIBusesResponse.parse_obj(body)
        buses_received = parsed.estimaciones

        buses_result = list()
        for bus_received in buses_received:
            # noinspection PyTypeChecker
            buses_result.append(Bus(
                line=bus_received.linea,
                route=bus_received.ruta,
                time_minutes=bus_received.minutos,
                distance_meters=bus_received.metros,
            ))

        # TODO Sort by distance, if available - method externally defined (in BusesResponse obj?)
        buses_result.sort(key=lambda bus: bus.time_minutes)
        return buses_result
