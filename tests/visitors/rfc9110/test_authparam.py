from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.authparam import AuthParam, AuthParamVisitor
from http_fields.visitors.rfc9110.quotedstring import QuotedString
from http_fields.visitors.rfc9110.token import Token


def test_authparam():
    auth_param = AuthParam(name="name", value="value")
    assert isinstance(auth_param.name, Token)
    assert auth_param.name == "name"
    assert isinstance(auth_param.value, (Token, QuotedString))
    assert auth_param.value == "value"


def test_authparam_realm():
    auth_param = AuthParam(name="realm", value="test")
    assert auth_param.name == "realm"
    assert auth_param.value == QuotedString("test")


def test_authparam_quotedstring():
    auth_param = AuthParam(name="name", value='"')
    assert isinstance(auth_param.value, QuotedString), repr(auth_param.value)


def test_authparam_str():
    auth_param = AuthParam(name="name", value="value")
    assert str(auth_param) == "name=value"


def test_authparam__eq():
    p1 = AuthParam("name", "value")
    p2 = AuthParam("name", "value")
    assert p1 == p2


def test_authparam__eq1():
    assert AuthParam("name", "value") != "test"


def test_authparam_visitor():
    src = "name=value"
    node = rfc9110.Rule("auth-param").parse_all(src)
    visitor = AuthParamVisitor()
    auth_param = visitor.visit(node)
    assert isinstance(auth_param, AuthParam)
    assert auth_param.name == "name"
    assert auth_param.value == "value"
