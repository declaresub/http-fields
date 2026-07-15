from datetime import datetime, timezone

from http_headers import LastModified


def test_lastmodified_parse():
    header = LastModified.parse("Tue, 03 Jan 2023 12:33:00 GMT")
    assert header.date == datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc)


def test_lastmodified_from_datetime():
    dt = datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc)
    assert LastModified(dt).date == dt


def test_lastmodified_value():
    header = LastModified(datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc))
    assert header.value == "Tue, 03 Jan 2023 12:33:00 GMT"
