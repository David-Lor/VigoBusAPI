__all__ = ("routes",)

from .v1.server import router as v1server


routes = [
    v1server,
]
