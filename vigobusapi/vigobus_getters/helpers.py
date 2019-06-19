"""HELPERS
Helper misc functions for external data management
"""

# # Native # #
import inspect

__all__ = ("get_package",)


def get_package(function) -> str:
    """Return the package name from the given object (usually a function).
    Only return the last package (inmediate first parent of the object).
    """
    return inspect.getmodule(function).__name__.split(".")[-1]
