import pytest

from http_headers import AcceptCharset


@pytest.mark.parametrize(
    "value, expected",
    [
        ("*; q=0.5", AcceptCharset(charsets=[("*", 0.5)])),
    ],
)
def test_acceptcharset_from_value(value: str, expected: AcceptCharset):
    accept_charset = AcceptCharset(value)
    assert accept_charset == expected


def test_acceptcharset():
    accept_charset = AcceptCharset(charsets=[("*", 0.5)])
    assert accept_charset.value == "*;q=0.5"
