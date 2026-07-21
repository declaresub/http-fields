"""A few functions used here and there in this package."""

import itertools
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import TypeVar, cast

S = TypeVar("S")
T = TypeVar("T")


def transform(
    items: Iterator[S | T], type_s: type[S], type_t: type[T]
) -> Iterator[tuple[S, T | None]]:
    try:
        item: S = cast(S, next(items))
    except StopIteration:
        return
    else:
        next_item: S | T | None = next(items, None)
        if isinstance(next_item, type_t):
            yield (item, cast(T, next_item))
            yield from transform(items, type_s, type_t)
        elif isinstance(next_item, type_s):
            yield (item, None)
            rest: Iterator[S | T] = itertools.chain([next_item], items)
            yield from transform(rest, type_s, type_t)
        elif next_item is None:
            yield (item, None)
        else:  # pragma: no cover
            raise AssertionError()


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
    fixdate_fmt = "%s, %02d %s %s %02d:%02d:%02d GMT"
    return fixdate_fmt % (
        day_name[pydate.weekday()],
        pydate.day,
        month_name[pydate.month - 1],
        pydate.year,
        pydate.hour,
        pydate.minute,
        pydate.second,
    )
