"""ROUTES BOOTSTRAP
Entrypoint for API routes setup
"""

from fastapi import FastAPI

from ._api import router as general_router
from ._stops_buses import router as stops_buses_router
from ._maps import router as maps_router


__all__ = ("setup_routes",)


def setup_routes(app: FastAPI):
    app.include_router(general_router)
    app.include_router(maps_router)
    app.include_router(stops_buses_router)
