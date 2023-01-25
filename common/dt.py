from datetime import datetime


def format_datetime(_dt: datetime) -> datetime:
    return _dt.isoformat(timespec="seconds")
