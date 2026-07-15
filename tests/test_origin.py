from http_headers import Header, Origin


def test_origin_parse():
    header = Origin.parse("https://example.com")
    assert header.origin == "https://example.com"
    assert header.value == "https://example.com"


def test_origin_create():
    assert isinstance(Header.create("origin", "https://example.com"), Origin)
