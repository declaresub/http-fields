from datetime import datetime, timedelta, timezone

import pytest

from http_headers import Date


def test_date_serializes_in_utc():
    # A tz-aware, non-UTC datetime must serialize as the equivalent UTC instant,
    # not its local wall clock relabelled "GMT" (regression: bug 8).
    eastern = timezone(timedelta(hours=-5))
    utc_date = Date(datetime(2021, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    eastern_date = Date(datetime(2021, 1, 1, 7, 0, 0, tzinfo=eastern))
    assert utc_date == eastern_date
    assert utc_date.value == "Fri, 01 Jan 2021 12:00:00 GMT"
    assert eastern_date.value == "Fri, 01 Jan 2021 12:00:00 GMT"


@pytest.mark.parametrize(
    "value, date",
    [
        (
            "Sun, 06 Nov 1994 08:49:37 GMT",
            datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc),
        ),  # RFC 822, updated by RFC 1123
        (
            "Sunday, 06-Nov-94 08:49:37 GMT",
            datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc),
        ),  # RFC 850, obsoleted by RFC 1036
        (
            "Sun Nov  6 08:49:37 1994",
            datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc),
        ),  # ANSI C asctime() format
    ],
)
def test_date_parse(value: str, date: datetime):
    header = Date.parse(value)
    assert header.date == date
    assert header.value == "Sun, 06 Nov 1994 08:49:37 GMT"


def test_date_from_datetime():
    date = datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc)
    header = Date(date)
    assert header.date == date
    assert header.value == "Wed, 21 Oct 2015 07:28:00 GMT"


def test_date_str():
    date = datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc)
    assert str(Date(date)) == "date: Wed, 21 Oct 2015 07:28:00 GMT"
