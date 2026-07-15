import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.token68 import Token68, Token68Visitor


def test_token68():
    token = Token68("token68")
    assert token == "token68"
    assert Token68(token) == "token68"


def test_token68_invalid():
    with pytest.raises(ValueError):
        Token68("bang!")


def test_token68visitor():
    src = "test"
    node = rfc9110.Rule("token68").parse_all(src)
    visitor = Token68Visitor()
    value = visitor.visit_token68(node)
    assert isinstance(value, Token68)
    assert value == src
