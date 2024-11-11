from datetime import date, datetime, timedelta


def get_today_as_datetime() -> datetime:
    return datetime.fromisoformat(date.today().isoformat())


def get_now_without_microsecond() -> datetime:
    return datetime.now().replace(microsecond=0)


def parse_td_str(td_str: str) -> timedelta:
    value, unit = int(td_str[:-1]), td_str[-1]

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
