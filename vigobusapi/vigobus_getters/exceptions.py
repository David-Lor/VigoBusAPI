"""EXCEPTIONS
Custom exceptions for the getters.
"""

__all__ = ("ParseError", "ParsingExceptions")

ParsingExceptions = (AttributeError, ValueError, TypeError, KeyError, AssertionError)
"""Exceptions that can be raised while parsing HTML returned by an external data source"""


class ParseError(Exception):
    """Exception raised when an error happened while parsing the data received from an external data source"""
    pass
