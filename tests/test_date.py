from datetime import datetime, timezone

import pytest

from http_headers import Date


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
