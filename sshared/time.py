from datetime import date, datetime, timedelta


def get_today_as_datetime() -> datetime:
    return datetime.fromisoformat(date.today().isoformat())


def get_now_without_microsecond() -> datetime:
    return datetime.now().replace(microsecond=0)


def get_datetime_before_now(td: timedelta) -> datetime:
    return datetime.now() - td
