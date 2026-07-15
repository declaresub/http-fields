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
