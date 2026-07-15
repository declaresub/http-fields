from datetime import datetime, timezone

import pytest

from http_headers import Expires


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
    header = Expires(value)
    assert header.expire_date == datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc)


def test_expires_value():
    header = Expires(datetime(2023, 1, 3, 12, 33, 0, tzinfo=timezone.utc))
    assert header.value == "Tue, 03 Jan 2023 12:33:00 GMT"


def test_expires_type_error():
    with pytest.raises(TypeError):
        Expires(1)  # type: ignore
