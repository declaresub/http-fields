import pytest

from http_headers import Connection
from http_headers.visitors.rfc9110 import Token


def test_connection_parse():
    header = Connection.parse("foo, bar")
    assert header.directives == (Token("foo"), Token("bar"))


def test_connection_from_tokens():
    header = Connection("foo", "bar")
    assert header.directives == (Token("foo"), Token("bar"))


def test_connection_value():
    assert Connection("foo", "bar").value == "foo,bar"


def test_connection_parse_bad_value():
    with pytest.raises(ValueError):
        Connection.parse("foo, , bar")


def test_connection_bad_token():
    with pytest.raises(ValueError):
        Connection("foo bar")
