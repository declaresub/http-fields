import pytest

from http_headers import Allow
from http_headers.visitors.rfc9110 import Token


def test_allow_parse():
    allow = Allow.parse("GET, POST")
    assert allow.methods == (Token("GET"), Token("POST"))


def test_allow_parse_invalid():
    with pytest.raises(ValueError):
        # semicolon is an invalid separator here.
        Allow.parse("GET; POST")


def test_allow_from_tokens():
    assert Allow("GET", "POST").value == "GET,POST"
