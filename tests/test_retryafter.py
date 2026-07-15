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
    ],
)
def test_retryafter_parse(value: str, expected: int | datetime):
    assert RetryAfter.parse(value).delay == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, 1),
        (
            datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc),
            datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc),
        ),
    ],
)
def test_retryafter_from_value(value: int | datetime, expected: int | datetime):
    assert RetryAfter(value).delay == expected


def test_retry_after_type_error():
    with pytest.raises(TypeError):
        RetryAfter(object())  # type: ignore[arg-type]


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
    assert RetryAfter(value).value == expected
