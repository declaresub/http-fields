import pytest

from http_headers import AuthenticationInfo, AuthParam


def test_authenticationinfo_empty():
    assert AuthenticationInfo().value == ""


def test_authenticationinfo_parse():
    header = AuthenticationInfo.parse("name=value, foo=bar")
    assert header == AuthenticationInfo(
        AuthParam("name", "value"), AuthParam("foo", "bar")
    )


def test_authenticationinfo_bad_value():
    with pytest.raises(ValueError):
        AuthenticationInfo.parse("name=value, ")
