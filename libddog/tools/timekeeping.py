from datetime import datetime, timedelta, timezone

import dateutil.parser


def parse_date(date_str: str) -> datetime:
    return dateutil.parser.parse(date_str)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def format_datetime_for_filename(dt: datetime) -> str:
    if dt.tzinfo and dt.tzinfo.utcoffset(dt) == timedelta(0):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    return dt.isoformat()


def time_since(delta: timedelta) -> str:
    fmt = ""

    if delta.total_seconds() < 1:
        ms = int(delta.total_seconds() * 1000)
        fmt = f"{ms} ms"

    elif delta.total_seconds() < 60:
        secs = int(delta.total_seconds())
        fmt = f"{secs} secs"

    elif delta.total_seconds() < 3600:
        mins = int(delta.total_seconds() / 60)
        fmt = f"{mins} mins"

    elif delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() / 3600)
        fmt = f"{hours} hours"

    elif delta.days < 30:
        days = delta.days
        fmt = f"{days} days"

    elif delta.days < 365:
        months = int(delta.days / 30)
        fmt = f"{months} months"

    else:
        years = int(delta.days / 365)
        fmt = f"{years} years"

    return fmt
