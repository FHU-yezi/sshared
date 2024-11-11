from datetime import date, datetime, timedelta


def to_date(x: datetime) -> date:
    return date.fromisoformat(x.isoformat())


def to_datetime(x: date) -> datetime:
    return datetime.fromisoformat(x.isoformat())


def without_microsecond(x: datetime) -> datetime:
    return x.replace(microsecond=0)


def parse_td_str(x: str) -> timedelta:
    value, unit = int(x[:-1]), x[-1]

    if unit == "s":
        return timedelta(seconds=value)
    if unit == "m":
        return timedelta(minutes=value)
    if unit == "h":
        return timedelta(hours=value)
    if unit == "d":
        return timedelta(days=value)

    raise ValueError


def get_datetime_before_now(td: timedelta) -> datetime:
    return datetime.now() - td
