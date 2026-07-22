from http_fields import ContentLocation, Header


def test_contentlocation_parse():
    value = "https://www.example.com/a/b"
    header = ContentLocation.parse(value)
    assert header.uri == value
    assert header.value == value


def test_contentlocation_create():
    assert isinstance(Header.create("content-location", "/a/b"), ContentLocation)
