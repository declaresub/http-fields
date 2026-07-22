from http_fields import (
    Header,
    ProxyAuthenticate,
    ProxyAuthenticationInfo,
    ProxyAuthorization,
)
from http_fields.visitors.rfc9110 import (
    AuthParam,
    AuthParamChallenge,
    TokenChallenge,
    TokenCredentials,
)


def test_proxy_authenticate_parse():
    header = ProxyAuthenticate.parse('Basic realm="test", Bearer')
    assert header.challenges == (
        AuthParamChallenge("Basic", [AuthParam("realm", "test")]),
        TokenChallenge("Bearer", None),
    )
    assert isinstance(Header.create("proxy-authenticate", "Bearer"), ProxyAuthenticate)


def test_proxy_authorization_parse():
    header = ProxyAuthorization.parse("Basic dXNlcm5hbWU6cGFzc3dvcmQ=")
    assert isinstance(header.credentials, TokenCredentials)
    assert header.credentials.scheme == "Basic"
    assert isinstance(
        Header.create("proxy-authorization", "Basic abc"), ProxyAuthorization
    )


def test_proxy_authentication_info_parse():
    header = ProxyAuthenticationInfo.parse("nextnonce=abc, qop=auth")
    assert header == ProxyAuthenticationInfo(
        AuthParam("nextnonce", "abc"), AuthParam("qop", "auth")
    )
    assert isinstance(
        Header.create("proxy-authentication-info", "a=b"), ProxyAuthenticationInfo
    )
