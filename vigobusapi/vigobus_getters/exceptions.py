"""EXCEPTIONS
Custom exceptions for the getters.
"""

__all__ = ("ParseError", "ParsingExceptions")

ParsingExceptions = (AttributeError, ValueError, KeyError)
"""Exceptions that can be raised while parsing HTML/XML returned by an external data source"""


class ParseError(Exception):
    pass
