from datetime import datetime, timezone

from http_fields import IfUnmodifiedSince


def test_ifunmodifiedsince_parse():
    header = IfUnmodifiedSince.parse("Sun, 06 Nov 1994 08:49:37 GMT")
    assert header.date == datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc)


def test_ifunmodifiedsince_from_datetime():
    dt = datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc)
    assert IfUnmodifiedSince(dt).date == dt


def test_ifunmodifiedsince_value():
    header = IfUnmodifiedSince.parse("Sun, 06 Nov 1994 08:49:37 GMT")
    assert header.value == "Sun, 06 Nov 1994 08:49:37 GMT"
