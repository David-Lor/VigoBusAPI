from typing import List, Dict, Optional

import fastapi
import pydantic

__all__ = ("Routes", "Tag", "Tags")

from ..utils import Utils
from vigobus.models.base import NEString


class Tag(pydantic.BaseModel):
    name: NEString
    description: str = ""


class Tags:

    # noinspection PyTypeChecker
    class V1:
        v1 = Tag(
            name="v1",
            description="API version v1",
        )
        server = Tag(
            name="server",
            description="Endpoints related with the API server.",
        )
        stops = Tag(
            name="stops",
            description="Stop entities represent data for physical stops where buses pass by."
        )
        buses = Tag(
            name="buses",
            description="Bus entities represent buses passing through stops, with a concrete journey "
                        "identified by line/route."
        )


class Routes:
    routes: List[fastapi.APIRouter] = list()
    _tags_kv: Dict[str, dict] = dict()
    tags: List[dict] = list()

    @classmethod
    def register(cls, router: fastapi.APIRouter = None, tags: Optional[List[Tag]] = None):
        if tags:
            cls.register_tags(tags)
            router.tags = [tag.name for tag in tags]
        cls.routes.append(router)

        return router

    @classmethod
    def register_tags(cls, tags: List[Tag]):
        for tag in tags:
            cls._tags_kv[tag.name] = tag.dict()
        cls.tags = list(cls._tags_kv.values())

    @classmethod
    def process_routes(cls):
        import vigobusapi.routes as pkg
        Utils.import_submodules(pkg, recursive=True)
        return cls.routes
