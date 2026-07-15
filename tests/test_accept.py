from http_headers import Accept
from http_headers.accept import AcceptType


def test_accept_parse():
    accept = Accept.parse("*/*")
    assert accept.accept_types == (AcceptType(type="*", subtype="*"),)


def test_accept_value():
    accept = Accept(AcceptType(type="*", subtype="*"))
    assert accept.value == "*/*"


def test_accept_empty():
    assert Accept().value == ""
