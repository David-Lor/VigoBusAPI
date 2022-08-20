import fastapi

from ..routes import Routes, Tags


router = fastapi.APIRouter(
    prefix="/v1/server"
)
Routes.register(router, tags=[Tags.V1.v1, Tags.V1.server])


@router.get("/status")
def v1_get_status():
    return "OK"
