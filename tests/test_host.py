import pytest

from http_headers import Host


@pytest.mark.parametrize(
    "src, hostname, port",
    [
        ("test.example.com", "test.example.com", None),
        ("test.example.com:81", "test.example.com", 81),
    ],
)
def test_host_parse(src: str, hostname: str, port: int | None):
    host = Host.parse(src)
    assert host.hostname == hostname
    assert host.port == port


@pytest.mark.parametrize(
    "host, expected",
    [
        (Host.parse("test.example.com:81"), "test.example.com:81"),
        (Host.parse("test.example.com"), "test.example.com"),
        (Host("example.com", 8080), "example.com:8080"),
    ],
)
def test_host_value(host: Host, expected: str):
    assert host.value == expected


def test_host_edge_cases():
    # Empty host / empty port must not crash or mistype (regression: bug 11).
    assert Host.parse(":80") == Host("", 80)
    empty_port = Host.parse("example.com:")
    assert empty_port.hostname == "example.com"
    assert empty_port.port is None


def test_host_case_insensitive_equality():
    # Host names are case-insensitive (regression: bug 21).
    assert Host.parse("EXAMPLE.com") == Host.parse("example.com")
    assert hash(Host.parse("EXAMPLE.com")) == hash(Host.parse("example.com"))
    assert Host("EXAMPLE.com") == Host("example.com")


def test_host_port_zero_serializes():
    # Port 0 is a valid port and must not be dropped (regression: bug 24 extra).
    assert Host("example.com", 0).value == "example.com:0"
