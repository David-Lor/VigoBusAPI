import fastapi

import vigobus.models
from ..routes import Routes, Tags


router = fastapi.APIRouter(
    prefix="/v1"
)
Routes.register(router, tags=[Tags.V1.v1, Tags.V1.buses])


@router.get(
    "/stops/{stop_id}/buses",
    tags=[Tags.V1.stops.name],
    description="Get real-time Buses that will arrive to a Stop, with their remaining time and distance.",
    response_model=vigobus.models.BusesResponse,
)
def get_stop_buses(stop_id: int, all_buses: bool = False) -> vigobus.models.BusesResponse:
    pass
