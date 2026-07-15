import pytest

from http_headers import AcceptEncoding, WeightedCoding


def test_accept_encoding_from_value():
    value = "gzip;q=1.0, identity; q=0.5, *;q=0"
    header = AcceptEncoding(value)
    assert header.codings == [
        WeightedCoding("gzip", 1.0),
        WeightedCoding("identity", 0.5),
        WeightedCoding("*", 0),
    ]


def test_accept_encoding_from_init():
    header = AcceptEncoding(codings=[("*", None)])
    assert header.value == "*"


def test_accept_encoding_bad_value():
    with pytest.raises(ValueError):
        AcceptEncoding('"gzip"')
