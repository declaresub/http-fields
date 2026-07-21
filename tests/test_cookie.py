from dataclasses import FrozenInstanceError

import pytest

from http_headers import Cookie
from http_headers.visitors.rfc6265 import CookiePair, CookieValue


def test_cookiepair_is_frozen():
    p = CookiePair("a", "b")
    with pytest.raises(FrozenInstanceError):
        p.value = CookieValue("c")  # type: ignore[misc]
    assert p == CookiePair("a", "b")
    assert repr(p) == "CookiePair(name=CookieName('a'), value=CookieValue('b'))"


def test_cookie_parse():
    cookie = Cookie.parse("a=b; c=d")
    assert cookie.pairs == (CookiePair("a", "b"), CookiePair("c", "d"))


def test_cookie_value():
    assert Cookie.parse("foo=bar").value == "foo=bar"


def test_cookie_trailing_semicolon():
    assert Cookie.parse("foo=bar;").value == "foo=bar"


def test_cookie_from_pairs():
    assert Cookie(("a", "b"), ("c", "d")).value == "a=b; c=d"


def test_cookie_empty_value():
    # An empty cookie-value must parse (regression: bug 3).
    cookie = Cookie.parse("a=")
    assert cookie.pairs == (CookiePair("a", ""),)
    assert cookie.value == "a="


def test_cookie_empty_value_among_others():
    cookie = Cookie.parse("a=; b=c")
    assert cookie.pairs == (CookiePair("a", ""), CookiePair("b", "c"))


def test_cookie_quoted_value_preserved():
    # DQUOTEs are part of the cookie-value and must be echoed (regression: bug 19).
    assert Cookie.parse('a="qv"').value == 'a="qv"'


def test_cookie_name_case_sensitive():
    # RFC 6265 cookie names are case-sensitive (regression: bug 20).
    assert Cookie.parse("SID=1") != Cookie.parse("sid=1")
    assert CookiePair("SID", "1") != CookiePair("sid", "1")
