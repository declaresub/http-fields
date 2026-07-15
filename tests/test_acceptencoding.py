import pytest

from http_headers import AcceptEncoding, WeightedCoding


def test_accept_encoding_parse():
    header = AcceptEncoding.parse("gzip;q=1.0, identity; q=0.5, *;q=0")
    assert header.codings == (
        WeightedCoding("gzip", 1.0),
        WeightedCoding("identity", 0.5),
        WeightedCoding("*", 0),
    )


def test_accept_encoding_from_codings():
    header = AcceptEncoding(("*", None))
    assert header.value == "*"


def test_accept_encoding_parse_bad_value():
    with pytest.raises(ValueError):
        AcceptEncoding.parse('"gzip"')
