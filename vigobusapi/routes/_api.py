"""API "General" Routes
"""

# # Installed # #
from fastapi import APIRouter, Response

__all__ = ("router",)

router = APIRouter()


@router.get("/status")
async def endpoint_status():
    return Response(
        content="OK",
        media_type="text/plain",
        status_code=200
    )
