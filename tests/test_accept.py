import pytest

from http_headers import Accept
from http_headers.accept import AcceptType


@pytest.mark.parametrize(
    "value, expected",
    [
        ("*/*", [AcceptType(type="*", subtype="*")]),
    ],
)
def test_accept_from_value(value: str, expected: list[AcceptType]):
    accept = Accept(value)
    assert accept.accept_types == expected


def test_accept():
    accept = Accept(accept_types=[AcceptType(type="*", subtype="*")])
    assert accept.value == "*/*"
