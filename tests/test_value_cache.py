"""The serialized value is computed once and cached (headers are immutable)."""

from http_fields import Age, ContentType, UserAgent


def test_value_is_cached_and_stable():
    ct = ContentType.parse("text/html; charset=utf-8")
    v1 = ct.value
    # cached_property stores the result in the instance __dict__ under "value"
    assert ct.__dict__["value"] == v1
    assert ct.value is v1
    # derived serializations remain correct and consistent
    assert str(ct) == f"Content-Type: {v1}"
    assert bytes(ct) == f"Content-Type: {v1}".encode("latin-1")
    assert ct.asgi_value == (b"Content-Type", v1.encode("latin-1"))


def test_cache_does_not_break_equality_or_hash():
    a, b = Age(60), Age(60)
    assert a == b
    assert hash(a) == hash(b)
    _ = a.value  # populate cache on one only
    assert a == b
    assert hash(a) == hash(b)


def test_cache_returns_same_object_across_accessors():
    ua = UserAgent.parse("Mozilla/5.0 (Windows NT 10.0)")
    v = ua.value
    # every accessor returns the one cached string object
    assert ua.value is v
    assert str(ua).endswith(v)
    assert ua.asgi_value[1] == v.encode("latin-1")
