from datetime import datetime, timezone

from http_fields import IfModifiedSince


def test_ifmodifiedsince_parse():
    header = IfModifiedSince.parse("Sun, 06 Nov 1994 08:49:37 GMT")
    assert header.date == datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc)


def test_ifmodifiedsince_from_datetime():
    dt = datetime(1994, 11, 6, 8, 49, 37, tzinfo=timezone.utc)
    assert IfModifiedSince(dt).date == dt


def test_ifmodifiedsince_value():
    header = IfModifiedSince.parse("Sun, 06 Nov 1994 08:49:37 GMT")
    assert header.value == "Sun, 06 Nov 1994 08:49:37 GMT"
