import fastapi


router = fastapi.APIRouter(
    prefix="/v1/server"
)


@router.get("/status")
def v1_get_status():
    return "OK"
