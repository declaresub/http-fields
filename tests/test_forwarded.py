from http_headers import Forwarded, ForwardedElement, Header


def test_forwarded_parse():
    header = Forwarded.parse(
        "for=192.0.2.60;proto=http;by=203.0.113.43, for=198.51.100.17"
    )
    assert header.elements == (
        ForwardedElement(
            (("for", "192.0.2.60"), ("proto", "http"), ("by", "203.0.113.43"))
        ),
        ForwardedElement((("for", "198.51.100.17"),)),
    )


def test_forwarded_value():
    header = Forwarded(ForwardedElement((("for", "192.0.2.60"), ("proto", "http"))))
    assert header.value == "for=192.0.2.60;proto=http"


def test_forwarded_create():
    assert isinstance(Header.create("forwarded", "for=192.0.2.60"), Forwarded)
