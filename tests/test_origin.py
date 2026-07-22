from http_fields import Header, Origin


def test_origin_parse():
    header = Origin.parse("https://example.com")
    assert header.origin == "https://example.com"
    assert header.value == "https://example.com"


def test_origin_null():
    # RFC 6454 / Fetch: an opaque origin serializes as "null" (abnf >= 2.6.0, issue #135).
    assert Origin.parse("null").origin == "null"


def test_origin_create():
    assert isinstance(Header.create("origin", "https://example.com"), Origin)
