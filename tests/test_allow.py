import pytest

from http_headers import Allow
from http_headers.allow import Method


def test_allow_parse():
    allow = Allow.parse("GET, POST")
    assert allow.methods == (Method("GET"), Method("POST"))


def test_allow_parse_invalid():
    with pytest.raises(ValueError):
        # semicolon is an invalid separator here.
        Allow.parse("GET; POST")


def test_allow_from_tokens():
    assert Allow(Method("GET"), Method("POST")).value == "GET,POST"


def test_allow_methods_case_sensitive():
    # HTTP methods are case-sensitive per RFC 9110 section 9.1 (regression: bug 24).
    assert Allow(Method("GET")) != Allow(Method("get"))
