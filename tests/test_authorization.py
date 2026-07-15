import pytest

from http_headers import Authorization
from http_headers.authorization import TokenCredentials


def test_authorization_from_value():
    value = "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
    header = Authorization(value)
    assert isinstance(header.credentials, TokenCredentials)
    assert header.credentials.scheme == "Basic"
    assert header.credentials.token == "dXNlcm5hbWU6cGFzc3dvcmQ="


def test_authorization_from_value_invalid():
    with pytest.raises(ValueError):
        Authorization("Bad Dog!")


def test_authorization_from_init():
    header = Authorization(
        credentials=TokenCredentials("Basic", "dXNlcm5hbWU6cGFzc3dvcmQ=")
    )
    assert header.value == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="


def test_authorization_from_init_no_args():
    with pytest.raises(ValueError):
        Authorization()
