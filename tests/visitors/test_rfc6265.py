from http_headers.visitors.rfc6265 import CookiePair


def test_cookie_pair_eq():
    assert CookiePair("name", "value") == CookiePair("Name", "value")


def test_cookie_pair_hash():
    assert isinstance(hash(CookiePair("name", "value")), int)
