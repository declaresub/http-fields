from datetime import datetime, timezone

import pytest

from http_headers import IfModifiedSince


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "Sun, 06 Nov 1994 08:49:37 GMT",
            datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc),
        ),
        (
            datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc),
            datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc),
        ),
    ],
)
def test_ifmodifiedsince_from_value(value: str | datetime, expected: datetime):
    header = IfModifiedSince(value)
    assert header.date == expected


def test_ifmodifiedsince_value():
    header = IfModifiedSince("Sun, 06 Nov 1994 08:49:37 GMT")
    assert header.value == "Sun, 06 Nov 1994 08:49:37 GMT"
