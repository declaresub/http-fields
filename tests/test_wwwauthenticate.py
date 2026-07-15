import pytest
from abnf.grammars import rfc9110

from http_headers import WWWAuthenticate
from http_headers.wwwauthenticate import (
    AuthParam,
    AuthParamChallenge,
    TokenChallenge,
    WWWAuthenticateVisitor,
)


def test_wwwauthenticate_parse():
    header = WWWAuthenticate.parse('Basic realm="test", Bearer')
    assert header.challenges == (
        AuthParamChallenge("Basic", [AuthParam("realm", "test")]),
        TokenChallenge("Bearer", None),
    )


def test_wwwauthenticate_parse_invalid():
    with pytest.raises(ValueError):
        WWWAuthenticate.parse("Bad Dog!")


def test_wwwauthenticate_from_challenges():
    header = WWWAuthenticate(AuthParamChallenge("Basic", [AuthParam("realm", "test")]))
    assert header.value == 'Basic realm="test"'


def test_wwwauthenticatevisitor():
    node = rfc9110.Rule("WWW-Authenticate").parse_all('Basic realm="test"')
    challenges = WWWAuthenticateVisitor().visit(node)
    assert challenges == [AuthParamChallenge("Basic", [AuthParam("realm", "test")])]
