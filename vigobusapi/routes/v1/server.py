import fastapi

from ..routes import Routes


router = fastapi.APIRouter(
    prefix="/v1/server"
)
Routes.register(router)


@router.get("/status")
def v1_get_status():
    return "OK"
