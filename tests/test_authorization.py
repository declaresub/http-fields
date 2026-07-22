import pytest

from http_fields import Authorization
from http_fields.authorization import TokenCredentials


def test_authorization_parse():
    header = Authorization.parse("Basic dXNlcm5hbWU6cGFzc3dvcmQ=")
    assert isinstance(header.credentials, TokenCredentials)
    assert header.credentials.scheme == "Basic"
    assert header.credentials.token == "dXNlcm5hbWU6cGFzc3dvcmQ="


def test_authorization_parse_invalid():
    with pytest.raises(ValueError):
        Authorization.parse("Bad Dog!")


def test_authorization_from_credentials():
    header = Authorization(TokenCredentials("Basic", "dXNlcm5hbWU6cGFzc3dvcmQ="))
    assert header.value == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="


def test_authorization_requires_credentials():
    with pytest.raises(TypeError):
        Authorization()  # type: ignore[call-arg]


def test_authorization_scheme_case_insensitive():
    # RFC 9110 section 11.1: auth-scheme is case-insensitive (round 2, bug 3).
    assert Authorization.parse("Basic dGVzdA==") == Authorization.parse(
        "basic dGVzdA=="
    )
    assert hash(Authorization.parse("Basic dGVzdA==")) == hash(
        Authorization.parse("basic dGVzdA==")
    )
