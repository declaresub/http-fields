from datetime import datetime, timezone

import pytest

from http_headers import LastModified


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "Tue, 03 Jan 2023 12:33:00 GMT",
            datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc),
            datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc),
        ),
    ],
)
def test_expires_from_value(value: str | datetime, expected: datetime):
    header = LastModified(value)
    assert header.date == datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc)


def test_expires_value():
    header = LastModified(datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc))
    assert header.value == "Tue, 03 Jan 2023 12:33:00 GMT"


def test_expires_type_error():
    with pytest.raises(TypeError):
        LastModified(1)  # type: ignore
