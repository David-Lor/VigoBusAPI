import contextlib
import datetime
from typing import Optional, Type

__all__ = ("Utils", "ErrorRetrier")

class Utils:
    @staticmethod
    def datetime_now() -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.timezone.utc)

    @staticmethod
    def unixtimestampseconds_to_datetime(ts: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)


class ErrorRetrier:
    """Wrapper that captures the exceptions within the wrapped code, not raising them, unless their type is given as
    `ignore_exceptions`.
    The last captured exception can be returned or raised from the public methods available.
    """

    def __init__(self, *ignore_exceptions: Type[Exception]):
        self._ignore_exceptions_types = ignore_exceptions or []
        self._exceptions = []

    @contextlib.contextmanager
    def wrap(self):
        try:
            yield self
        except Exception as ex:
            self.add_exception(ex)

    def add_exception(self, ex):
        """Add the given exception instance to the ErrorRetrier list of captured exceptions,
        if not given as an ignored exception type.
        """
        if type(ex) not in self._ignore_exceptions_types:
            self._exceptions.append(ex)

    @property
    def last_exception(self) -> Optional[Exception]:
        """Last exception captured, if any.
        """
        if self._exceptions:
            return self._exceptions[-1]

    def raise_last_exception(self):
        """Raise the last exception captured, if any.
        """
        ex = self.last_exception
        if ex:
            raise ex
