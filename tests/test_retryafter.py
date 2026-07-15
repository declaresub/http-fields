from datetime import datetime, timezone

import pytest

from http_headers import RetryAfter


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "Wed, 21 Oct 2015 07:28:00 GMT",
            datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc),
        ),
        ("7", 7),
        (1, 1),
        (
            datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc),
            datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc),
        ),
    ],
)
def test_retryafter_from_value(value: str, expected: int | datetime):
    header = RetryAfter(value)
    assert header.delay == expected


def test_retryafter_from_value_2():
    value = "7"
    header = RetryAfter(value)
    assert header.delay == 7


def test_retry_after_type_error():
    with pytest.raises(TypeError):
        RetryAfter(object())  # type: ignore


def test_retry_after_negative_delay():
    with pytest.raises(ValueError):
        RetryAfter(-1)


@pytest.mark.parametrize(
    "value, expected",
    [
        (30, "30"),
        (
            datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc),
            "Wed, 21 Oct 2015 07:28:00 GMT",
        ),
    ],
)
def test_retry_after_value(value: int | datetime, expected: str):
    header = RetryAfter(value)
    assert header.value == expected
