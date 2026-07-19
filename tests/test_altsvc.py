from http_headers import AltSvc, AltUsed, AltValue, Header


def test_altsvc_parse():
    header = AltSvc.parse('h2="alt.example.com:443"; ma=3600, h3=":443"')
    assert header.values == (
        AltValue("h2", '"alt.example.com:443"', (("ma", "3600"),)),
        AltValue("h3", '":443"'),
    )


def test_altsvc_clear():
    header = AltSvc.parse("clear")
    assert header.clear is True
    assert header.value == "clear"


def test_altused_parse():
    assert AltUsed.parse("alternate.example.net:443").authority == (
        "alternate.example.net:443"
    )


def test_altsvc_create():
    assert isinstance(Header.create("alt-svc", 'h2=":443"'), AltSvc)
    assert isinstance(Header.create("alt-used", "example.com:443"), AltUsed)
