import pytest

from http_headers import Authorization
from http_headers.authorization import TokenCredentials


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
