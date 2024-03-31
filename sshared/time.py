from datetime import date, datetime


def get_today_as_datetime() -> datetime:
    return datetime.fromisoformat(date.today().isoformat())
