"""EXCEPTIONS
Exceptions used on the project
"""

__all__ = ("VigoBusAPIException", "StopNotExist", "StopNotFound")


class VigoBusAPIException(Exception):
    """Base exception for the project custom exceptions"""
    pass


class StopNotExist(VigoBusAPIException):
    """The Stop does not physically exist (as reported by an external trusted API/data source)"""
    pass


class StopNotFound(VigoBusAPIException):
    """The Stop was not found on a local data source, but might physically exist"""
    pass
