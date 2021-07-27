from datetime import datetime

import dateutil


def utcnow() -> datetime:
    return datetime.now(dateutil.tz.tzutc())  # type: ignore
