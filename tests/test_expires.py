from datetime import datetime, timezone

from http_fields import Expires


def test_expires_parse():
    header = Expires.parse("Tue, 03 Jan 2023 12:33:00 GMT")
    assert header.date == datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc)


def test_expires_from_datetime():
    dt = datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc)
    assert Expires(dt).date == dt


def test_expires_value():
    header = Expires(datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc))
    assert header.value == "Tue, 03 Jan 2023 12:33:00 GMT"
