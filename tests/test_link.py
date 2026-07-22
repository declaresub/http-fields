from http_fields import Header, Link, LinkValue


def test_link_parse():
    header = Link.parse('<https://example.com/1>; rel="next"; title="Next"')
    assert header.links == (
        LinkValue("https://example.com/1", (("rel", '"next"'), ("title", '"Next"'))),
    )


def test_link_roundtrip():
    value = '<https://example.com/1>; rel="next", <https://example.com/2>; rel="prev"'
    assert Link.parse(value).value == value


def test_link_create():
    assert isinstance(Header.create("link", "<https://example.com>; rel=next"), Link)
