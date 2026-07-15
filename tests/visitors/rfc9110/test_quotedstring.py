import pytest
from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.quotedstring import (
    QuotedPairVisitor,
    QuotedString,
    QuotedStringVisitor,
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
    node = rfc9110.Rule("quoted-pair").parse_all(src)
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
    node = rfc9110.Rule("quoted-string").parse_all(src)
    assert QuotedStringVisitor().visit(node) == QuotedString("\\test")
