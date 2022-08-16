__all__ = ("BaseVigobusException", "DatasourceMethodUnavailableException", "StopNotExistException")


class BaseVigobusException(Exception):
    pass


class DatasourceMethodUnavailableException(BaseVigobusException):
    pass


class StopNotExistException(BaseVigobusException):
    def __init__(self, stop_id: int):
        self.stop_id = stop_id
