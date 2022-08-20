import fastapi

import vigobus.models
import vigobus.exceptions
from ..routes import Routes, Tags
from vigobusapi.services.controller import VigobusController

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
async def get_stop_buses(stop_id: int, request: fastapi.Request, all_buses: bool = False) -> vigobus.models.BusesResponse:
    controller = VigobusController.get_from_request(request)
    try:
        return await controller.get_stop_buses(stop_id, all_buses)
    except vigobus.exceptions.StopNotExistException:
        raise fastapi.HTTPException(status_code=404, detail="Stop not exists")
