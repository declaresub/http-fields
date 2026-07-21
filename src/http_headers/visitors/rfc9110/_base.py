"""A few functions used here and there in this package."""

from collections.abc import Iterator
from datetime import datetime, timezone
from typing import TypeVar, cast

S = TypeVar("S")
T = TypeVar("T")


def transform(
    items: Iterator[S | T], type_s: type[S], type_t: type[T]
) -> Iterator[tuple[S, T | None]]:
    """Pair each ``type_s`` item with the optional ``type_t`` item that follows it.

    Iterative (not recursive) so an arbitrarily long stream — e.g. a very long
    ``Accept`` header — cannot exhaust the call stack.
    """
    pending: S | None = None
    for item in items:
        if isinstance(item, type_t):
            if pending is None:  # pragma: no cover - a type_t with no preceding type_s
                raise AssertionError()
            yield (pending, cast(T, item))
            pending = None
        elif isinstance(item, type_s):
            if pending is not None:
                yield (pending, None)
            pending = item
        else:  # pragma: no cover
            raise AssertionError()
    if pending is not None:
        yield (pending, None)


def imf_fixdate(pydate: datetime):
    """
    Converts a datetime object to a fixdate string.
    """

    # HTTP dates are expressed in GMT/UTC. Convert tz-aware datetimes to UTC so the
    # printed wall-clock fields match the "GMT" label; naive datetimes are assumed
    # to already be UTC.
    if pydate.tzinfo is not None:
        pydate = pydate.astimezone(timezone.utc)

    day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    month_name = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    fixdate_fmt = "%s, %02d %s %04d %02d:%02d:%02d GMT"
    return fixdate_fmt % (
        day_name[pydate.weekday()],
        pydate.day,
        month_name[pydate.month - 1],
        pydate.year,
        pydate.hour,
        pydate.minute,
        pydate.second,
    )
