from http_headers import CacheControl, CacheDirective


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
