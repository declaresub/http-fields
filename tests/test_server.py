from http_fields import Header, Server


def test_server_parse():
    value = "Apache/2.4.1 (Unix)"
    assert Server.parse(value).value == value


def test_server_create():
    assert isinstance(Header.create("server", "nginx/1.0"), Server)
