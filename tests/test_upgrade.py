from http_headers import Header, Protocol, Upgrade


def test_upgrade_parse():
    header = Upgrade.parse("HTTP/2, WebSocket")
    assert header.protocols == (Protocol("HTTP", "2"), Protocol("WebSocket"))


def test_upgrade_value():
    assert Upgrade(Protocol("HTTP", "2"), Protocol("WebSocket")).value == (
        "HTTP/2, WebSocket"
    )


def test_upgrade_create():
    assert isinstance(Header.create("upgrade", "h2c"), Upgrade)
