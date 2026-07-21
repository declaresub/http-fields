import pytest

from http_headers import CacheControl, CacheDirective


def test_cachecontrol_bare_max_stale():
    # RFC 9111 section 5.2.1.2: max-stale may appear with no value (regression: bug 9).
    cc = CacheControl.parse("max-stale")
    assert cc.max_stale is True
    assert cc.value == "max-stale"


def test_cachecontrol_bounded_max_stale():
    cc = CacheControl.parse("max-stale=60")
    assert cc.max_stale == 60
    assert cc.value == "max-stale=60"


def test_cachecontrol_bare_max_age_rejected():
    # max-age requires a value; a valueless one is malformed and must raise
    # ValueError (not TypeError).
    with pytest.raises(ValueError):
        CacheControl.parse("max-age")


def test_cachecontrol_parse():
    header = CacheControl.parse("max-age=31536000, immutable, foo=bar")
    assert header.immutable is True
    assert header.max_age == 31536000
    assert header.cache_extension == (CacheDirective("foo", "bar"),)


def test_cachecontrol_from_init():
    header = CacheControl(
        immutable=True,
        max_age=31536000,
        cache_extension=(CacheDirective("foo", "bar"),),
    )
    assert header.immutable is True
    assert header.max_age == 31536000
    assert header.max_stale is None
    assert header.cache_extension == (CacheDirective("foo", "bar"),)


def test_cachecontrol_value():
    header = CacheControl(immutable=True, max_age=31536000)
    assert header.value == "immutable,max-age=31536000"


def test_cachecontrol_extension_roundtrip():
    # s-maxage=0 must survive (falsy-0), and extension directives serialize.
    assert CacheControl.parse("s-maxage=0, foo=bar").value == "s-maxage=0,foo=bar"
