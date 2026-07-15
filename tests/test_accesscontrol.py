import pytest

from http_headers import (
    AccessControlAllowCredentials,
    AccessControlAllowHeaders,
    AccessControlAllowMethods,
    AccessControlAllowOrigin,
    AccessControlExposeHeaders,
    AccessControlMaxAge,
    AccessControlRequestHeaders,
    AccessControlRequestMethod,
    Header,
)


def test_allow_methods():
    header = AccessControlAllowMethods.parse("GET, POST")
    assert header.items == ("GET", "POST")
    assert AccessControlAllowMethods("GET", "POST").value == "GET, POST"


def test_allow_headers():
    header = AccessControlAllowHeaders.parse("X-Custom, Content-Type")
    assert header.items == ("X-Custom", "Content-Type")


def test_request_headers():
    assert AccessControlRequestHeaders.parse("X-Foo").items == ("X-Foo",)


def test_expose_headers():
    assert AccessControlExposeHeaders("X-Foo", "X-Bar").value == "X-Foo, X-Bar"


def test_allow_origin():
    assert AccessControlAllowOrigin.parse("*").origin == "*"
    assert AccessControlAllowOrigin.parse("https://example.com").value == (
        "https://example.com"
    )


def test_request_method():
    assert AccessControlRequestMethod.parse("GET").method == "GET"


def test_max_age():
    header = AccessControlMaxAge.parse("600")
    assert header.max_age == 600
    assert AccessControlMaxAge(600).value == "600"


def test_max_age_negative():
    with pytest.raises(ValueError):
        AccessControlMaxAge(-1)


def test_allow_credentials():
    assert AccessControlAllowCredentials.parse("true").value == "true"
    with pytest.raises(ValueError):
        AccessControlAllowCredentials.parse("false")


def test_cors_create():
    assert isinstance(
        Header.create("access-control-allow-origin", "*"), AccessControlAllowOrigin
    )
    assert isinstance(
        Header.create("access-control-max-age", "600"), AccessControlMaxAge
    )
