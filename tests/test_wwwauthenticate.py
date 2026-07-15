import pytest
from abnf.grammars import rfc9110

from http_headers import WWWAuthenticate
from http_headers.wwwauthenticate import (
    AuthParam,
    AuthParamChallenge,
    TokenChallenge,
    WWWAuthenticateVisitor,
)


def test_WWWAuthenticate_from_value():
    value = 'Basic realm="test", Bearer'
    header = WWWAuthenticate(value)
    assert header.challenges == [
        AuthParamChallenge("Basic", [AuthParam("realm", "test")]),
        TokenChallenge("Bearer", None),
    ]


def test_WWWAuthenticate_from_value_invalid():
    value = "Bad Dog!"
    with pytest.raises(ValueError):
        WWWAuthenticate(value)


def test_WWWAuthenticate_from_init():
    header = WWWAuthenticate(
        challenges=[AuthParamChallenge("Basic", [AuthParam("realm", "test")])]
    )
    assert header.value == 'Basic realm="test"'


def test_wwwauthenticatevisitor():
    src = 'Basic realm="test"'
    node = rfc9110.Rule("WWW-Authenticate").parse_all(src)
    visitor = WWWAuthenticateVisitor()
    challenges = visitor.visit(node)
    assert challenges == [
        AuthParamChallenge("Basic", [AuthParam("realm", "test")]),
        # TokenChallenge("Bearer", None),
    ]
