from datetime import date, datetime


def get_today_as_datetime() -> datetime:
    return datetime.fromisoformat(date.today().isoformat())


def get_now_without_microsecond() -> datetime:
    return datetime.now().replace(microsecond=0)
