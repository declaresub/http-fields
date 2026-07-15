from http_headers import Header, Via, ViaElement


def test_via_parse():
    header = Via.parse("1.1 vegur, HTTP/1.1 proxy.example.com:80")
    assert header.elements == (
        ViaElement("1.1", "vegur"),
        ViaElement("HTTP/1.1", "proxy.example.com:80"),
    )


def test_via_parse_comment():
    header = Via.parse("1.0 fred (Apache/1.1)")
    assert header.elements == (ViaElement("1.0", "fred", "(Apache/1.1)"),)


def test_via_value():
    assert Via(ViaElement("1.1", "vegur")).value == "1.1 vegur"


def test_via_create():
    assert isinstance(Header.create("via", "1.1 example.com"), Via)
