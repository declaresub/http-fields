import pytest

from http_headers import AuthenticationInfo, AuthParam


def test_authenticationinfo():
    assert AuthenticationInfo()


def test_authenticationinfo_fromvalue():
    value = "name=value, foo=bar"
    header = AuthenticationInfo(value)
    assert header == AuthenticationInfo(
        auth_params=[AuthParam("name", "value"), AuthParam("foo", "bar")]
    )


def test_authenticationinfo_bad_value():
    value = "name=value, "
    with pytest.raises(ValueError):
        AuthenticationInfo(value)
