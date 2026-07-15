import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.token import Token, TokenVisitor


def test_token():
    s = "token"
    t = Token(s)
    assert t == s
    assert Token(t) == s


def test_visit_token():
    src = "token"
    node = rfc9110.Rule("token").parse_all(src)
    visitor = TokenVisitor()
    qs = visitor.visit(node)
    assert isinstance(qs, Token)
    assert qs == src


def test_token_invalid():
    with pytest.raises(ValueError):
        Token('"')
