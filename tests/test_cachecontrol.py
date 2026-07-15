from http_headers import CacheControl, CacheDirective


def test_cachecontrol_from_value():
    value = "max-age=31536000, immutable, foo=bar"
    header = CacheControl(value)
    assert header.immutable is True
    assert header.max_age == 31536000
    assert header.cache_extension == [CacheDirective("foo", "bar")]


def test_cachecontrol_from_init():
    header = CacheControl(
        immutable=True, max_age=31536000, cache_extension=[CacheDirective("foo", "bar")]
    )
    assert header.immutable is True
    assert header.max_age == 31536000
    assert header.max_stale is None
    assert header.cache_extension == [CacheDirective("foo", "bar")]


def test_cachecontrol_value():
    header = CacheControl(immutable=True, max_age=31536000)
    assert header.value == "immutable,max-age=31536000"
