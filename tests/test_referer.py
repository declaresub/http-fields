from http_headers import Header, Referer


def test_referer_parse():
    value = "https://www.example.com/a/b"
    header = Referer.parse(value)
    assert header.uri == value
    assert header.value == value


def test_referer_create():
    assert isinstance(Header.create("referer", "/a/b"), Referer)
