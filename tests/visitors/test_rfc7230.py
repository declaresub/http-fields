import pytest

from http_headers.visitors.rfc7230 import (
    QuotedPairVisitor,
    QuotedString,
    QuotedStringVisitor,
    Token,
    TokenVisitor,
    rfc7230,
)


@pytest.mark.parametrize(
    "src, expected",
    [
        ("\\\t", "\t"),
        ("\\ ", " "),
        ("\\X", "X"),
        ("\\Ç", "Ç"),
    ],
)
def test_quotedpair_visitor(src: str, expected: str):
    node = rfc7230.Rule("quoted-pair").parse_all(src)
    assert QuotedPairVisitor().visit(node) == expected


@pytest.mark.parametrize(
    "src, expected",
    [
        ("test", '"test"'),
        ('"test"', '"test"'),
        ("\\test", '"\\\\test"'),
        ("", '""'),
        ('"', '"\\""'),
    ],
)
def test_quotedstring_from_str(src: str, expected: str):
    assert str(QuotedString(src)) == expected


def test_quotedstring_from_quotedstring():
    qs = QuotedString("test")
    assert QuotedString(qs) is qs


def test_quotedstring_visitor():
    src = '"\\\\test"'
    node = rfc7230.Rule("quoted-string").parse_all(src)
    assert QuotedStringVisitor().visit(node) == QuotedString("\\test")


def test_token():
    s = "token"
    t = Token(s)
    assert t == s
    assert Token(t) == s


def test_visit_token():
    src = "token"
    node = rfc7230.Rule("token").parse_all(src)
    visitor = TokenVisitor()
    qs = visitor.visit(node)
    assert isinstance(qs, Token)
    assert qs == src


def test_token_invalid():
    with pytest.raises(ValueError):
        Token('"')
