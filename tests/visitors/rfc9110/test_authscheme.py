import pytest

from http_headers.visitors.rfc9110.authscheme import AuthScheme


def test_authscheme():
    scheme = AuthScheme("Basic")
    assert scheme == "Basic"
    assert AuthScheme(scheme) == "Basic"


def test_authscheme_invalid():
    with pytest.raises(ValueError):
        AuthScheme('"')
