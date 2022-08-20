import fastapi

import vigobus.models
from ..routes import Routes, Tags
from vigobusapi.services.controller import VigobusController

router = fastapi.APIRouter(
    prefix="/v1"
)
Routes.register(router, tags=[Tags.V1.v1, Tags.V1.stops])


@router.get(
    "/stops/{stop_id}/data",
    description="Get static data for a physical buses Stop.",
    response_model=vigobus.models.Stop,
)
async def get_stop_data(stop_id: int, request: fastapi.Request) -> vigobus.models.Stop:
    controller = VigobusController.get_from_request(request)
    stop = await controller.get_stop_data(stop_id)
    if not stop:
        raise fastapi.HTTPException(status_code=404, detail="Stop not exists")

    return stop
