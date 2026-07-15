import pytest

from http_headers import Allow
from http_headers.visitors.rfc9110 import Token


def test_allow_from_value():
    allow = Allow("GET, POST")
    assert allow.methods == [Token("GET"), Token("POST")]


def test_allow_from_value_invalid():
    with pytest.raises(ValueError):
        # semicolon is an invalid separator here.
        Allow("GET; POST")


def test_allow_from_obj():
    allow = Allow(methods=["GET", "POST"])
    assert allow.value == "GET,POST"
