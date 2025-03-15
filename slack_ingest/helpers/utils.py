from datetime import datetime, timezone

from pympler import asizeof as pympler_size


def ts2datetime(ts=1571321692.001200) -> datetime:
    ts = float(ts)
    return datetime.fromtimestamp(ts, timezone.utc)


# def ts2ymd(ts=1571321692.001200):
#     return ts2datetime(float(ts)).strftime("%Y-%m-%d")


def size_of_mb(obj) -> float:
    # return get_size(obj) / (1024 * 1024) seems to not reflect different sizes
    return pympler_size.asizeof(obj) / (1024 * 1024)
