from typing import List

import fastapi

__all__ = ("Routes",)

from vigobusapi.utils import Utils


class Routes:
    routes: List[fastapi.APIRouter] = list()

    @classmethod
    def register(cls, router: fastapi.APIRouter = None):
        # if not router:
        #     def wrapper(_router: fastapi.APIRouter):
        #         cls.register(_router)
        #         return _router
        #     return wrapper

        print("Register router", router)
        cls.routes.append(router)
        return router

    @classmethod
    def process_routes(cls):
        import vigobusapi.routes as pkg
        Utils.import_submodules(pkg, recursive=True)
        return cls.routes
