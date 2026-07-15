import pytest

from http_headers import Host


@pytest.mark.parametrize(
    "src, expected",
    [
        ("test.example.com", ("test.example.com", None)),
        ("test.example.com:81", ("test.example.com", 81)),
    ],
)
def test_host_from_value(src: str, expected: tuple[str, int | None]):
    host = Host("test.example.com")
    assert host.hostname, host.port == expected


@pytest.mark.parametrize(
    "host, expected",
    [
        (Host("test.example.com:81"), "test.example.com:81"),
        (Host("test.example.com"), "test.example.com"),
    ],
)
def test_host_value(host: Host, expected: str):
    assert host.value == expected
