from http_fields.visitors.rfc6265 import CookiePair


def test_cookie_pair_eq():
    assert CookiePair("name", "value") == CookiePair("name", "value")


def test_cookie_pair_name_case_sensitive():
    # RFC 6265 cookie names are case-sensitive (regression: bug 20).
    assert CookiePair("name", "value") != CookiePair("Name", "value")


def test_cookie_pair_hash():
    assert isinstance(hash(CookiePair("name", "value")), int)
