from abnf.grammars import rfc9110

from http_headers.visitors.rfc9110.authparam import AuthParam
from http_headers.visitors.rfc9110.authscheme import AuthScheme
from http_headers.visitors.rfc9110.challenge import (
    AuthParamChallenge,
    ChallengeVisitor,
    TokenChallenge,
)
from http_headers.visitors.rfc9110.token68 import Token68


def test_tokenchallenge():
    challenge = TokenChallenge("Basic", "token")
    assert isinstance(challenge.scheme, AuthScheme)
    assert isinstance(challenge.token, Token68)


def test_tokenchallenge_str():
    challenge = TokenChallenge("Test", "token")
    assert str(challenge) == "Test token"


def test_tokenchallenge_eq():
    assert TokenChallenge("Bearer", None) == TokenChallenge("Bearer", None)
    assert TokenChallenge("Bearer", None) != TokenChallenge("Bearer", "nonce")
    assert TokenChallenge("Bearer", None) != "challenge"


def test_authparamchallenge():
    challenge = AuthParamChallenge("Basic", [AuthParam("realm", "test")])
    assert isinstance(challenge.scheme, AuthScheme)
    assert challenge.auth_params == (AuthParam("realm", "test"),)


def test_authparamchallenge_str():
    challenge = AuthParamChallenge("Basic", [AuthParam("realm", "test")])
    assert str(challenge) == 'Basic realm="test"'


def test_authparamchallenge_eq():
    assert AuthParamChallenge(
        "Basic", [AuthParam("realm", "test")]
    ) == AuthParamChallenge("Basic", [AuthParam("realm", "test")])
    assert AuthParamChallenge(
        "Basic", [AuthParam("realm", "test")]
    ) != AuthParamChallenge("Basic", [AuthParam("realm", "foo")])
    assert AuthParamChallenge("Basic", [AuthParam("realm", "test")]) != "challenge"


def test_challenge_visitor_auth_param():
    src = 'Test realm="test"'
    node = rfc9110.Rule("challenge").parse_all(src)
    visitor = ChallengeVisitor()
    challenge = visitor.visit(node)
    assert challenge == AuthParamChallenge("Test", [AuthParam("realm", "test")])


def test_challenge_visitor_token():
    src = "Bearer nonce"
    node = rfc9110.Rule("challenge").parse_all(src)
    visitor = ChallengeVisitor()
    challenge = visitor.visit(node)
    assert challenge == TokenChallenge("Bearer", "nonce")


def test_challenge_visitor_token1():
    src = "Bearer"
    node = rfc9110.Rule("challenge").parse_all(src)
    visitor = ChallengeVisitor()
    challenge = visitor.visit(node)
    assert challenge == TokenChallenge("Bearer", None)
