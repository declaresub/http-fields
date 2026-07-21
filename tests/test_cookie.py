from http_headers import Cookie
from http_headers.visitors.rfc6265 import CookiePair


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
