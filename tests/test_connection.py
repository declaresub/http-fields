import pytest

from http_headers import Connection
from http_headers.visitors.rfc9110.token import Token


def test_connection_from_value():
    header = Connection("foo, bar")
    assert header.directives == [Token("foo"), Token("bar")]


def test_connection_from_values():
    header = Connection("foo", "bar")
    assert header.directives == [Token("foo"), Token("bar")]


def test_connection_value():
    header = Connection("foo", "bar")
    assert header.value == "foo,bar"


def test_connection_bad_value():
    with pytest.raises(ValueError):
        Connection("foo, , bar")
