import fastapi

import vigobus.models
from ..routes import Routes, Tags


router = fastapi.APIRouter(
    prefix="/v1"
)
Routes.register(router, tags=[Tags.V1.v1, Tags.V1.stops])


@router.get(
    "/stops/{stop_id}/data",
    description="Get static data for a physical buses Stop.",
    response_model=vigobus.models.Stop,
)
async def get_stop_data(stop_id: int) -> vigobus.models.Stop:
    pass
