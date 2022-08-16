import datetime


class Utils:
    @staticmethod
    def datetime_now() -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.timezone.utc)

    @staticmethod
    def unixtimestampseconds_to_datetime(ts: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
