from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110.authorization import (
    AuthParamCredentials,
    CredentialsVisitor,
    TokenCredentials,
)
from http_fields.visitors.rfc9110.authparam import AuthParam
from http_fields.visitors.rfc9110.authscheme import AuthScheme


def test_authparamcredentials():
    auth_params = [
        AuthParam("username", "Mufasa"),
        AuthParam("realm", "http-auth@example.org"),
        AuthParam("uri", "/dir/index.html"),
        AuthParam("algorithm", "MD5"),
        AuthParam("nonce", "7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v"),
        AuthParam("nc", "00000001"),
        AuthParam("cnonce", "f2/wE4q74E6zIJEtWaHKaf5wv/H5QzzpXusqGemxURZJ"),
        AuthParam("qop", "auth"),
        AuthParam("response", "8ca523f5e9506fed4657c9700eebdbec"),
        AuthParam("opaque", "FQhe/qaU925kfnzjCev0ciny7QMkPqMAFRtzCUYo5tdS"),
    ]

    credentials = AuthParamCredentials("Digest", auth_params)
    assert isinstance(credentials.scheme, AuthScheme)
    assert credentials.auth_params == tuple(auth_params)


def test_authparamcredentials_str():
    auth_params = [
        AuthParam("username", "Mufasa"),
        AuthParam("realm", "http-auth@example.org"),
        AuthParam("uri", "/dir/index.html"),
        AuthParam("algorithm", "MD5"),
        AuthParam("nonce", "7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v"),
        AuthParam("nc", "00000001"),
        AuthParam("cnonce", "f2/wE4q74E6zIJEtWaHKaf5wv/H5QzzpXusqGemxURZJ"),
        AuthParam("qop", "auth"),
        AuthParam("response", "8ca523f5e9506fed4657c9700eebdbec"),
        AuthParam("opaque", "FQhe/qaU925kfnzjCev0ciny7QMkPqMAFRtzCUYo5tdS"),
    ]
    credentials = AuthParamCredentials("Digest", auth_params)
    assert (
        str(credentials)
        == 'Digest username=Mufasa,realm="http-auth@example.org",uri="/dir/index.html",algorithm=MD5,nonce="7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v",nc=00000001,cnonce="f2/wE4q74E6zIJEtWaHKaf5wv/H5QzzpXusqGemxURZJ",qop=auth,response=8ca523f5e9506fed4657c9700eebdbec,opaque="FQhe/qaU925kfnzjCev0ciny7QMkPqMAFRtzCUYo5tdS"'
    )


def test_authparamcredentials_eq():
    assert AuthParamCredentials(
        "Basic", [AuthParam("realm", "test")]
    ) == AuthParamCredentials("Basic", [AuthParam("realm", "test")])
    assert AuthParamCredentials(
        "Basic", [AuthParam("realm", "test")]
    ) != AuthParamCredentials("Basic", [AuthParam("realm", "foo")])
    assert AuthParamCredentials("Basic", [AuthParam("realm", "test")]) != "challenge"


def test_tokencredentials_eq():
    assert TokenCredentials("Bearer", None) == TokenCredentials("Bearer", None)
    assert TokenCredentials("Bearer", None) != TokenCredentials("Bearer", "nonce")
    assert TokenCredentials("Bearer", None) != "challenge"


def test_credentials_visitor_auth_param():
    src = 'Test realm="test"'
    node = rfc9110.Rule("credentials").parse_all(src)
    visitor = CredentialsVisitor()
    challenge = visitor.visit(node)
    assert challenge == AuthParamCredentials("Test", [AuthParam("realm", "test")])


def test_credentials_visitor_token():
    src = "Bearer"
    node = rfc9110.Rule("credentials").parse_all(src)
    visitor = CredentialsVisitor()
    challenge = visitor.visit(node)
    assert challenge == TokenCredentials("Bearer", None)
