import pytest

from http_headers import Header, Host


def test_header_init():
    name = "X-Test"
    value = "example.com"
    header = Header(name, value=value)
    assert header.name == name
    assert header.value == value


def test_header_init_bad_name():
    with pytest.raises(AssertionError):
        Header(6, value="")  # type: ignore


def test_header_init_bad_value():
    with pytest.raises(AssertionError):
        Header("X-Test", value=6)  # type: ignore


def test_header_init_invalid_name():
    name = "X-Header abcd"
    value = "test"
    with pytest.raises(ValueError):
        Header(name, value=value)


def test_header_init_invalid_value():
    name = "X-Header"
    value = "test\rfail"
    with pytest.raises(ValueError):
        Header(name, value=value)


def test_header_bytes():
    header = Header("Foo", "bar")
    assert bytes(header) == b"Foo: bar"


def test_header_asgi_value():
    header = Header("Foo", "bar")
    assert header.asgi_value == (b"Foo", b"bar")


def test_header_create():
    header = Header.create("Foo", "bar")
    assert header.name == "Foo"
    assert header.value == "bar"


class XFoo(Header):
    name = "X-Foo"

    def __init__(self, value: str):
        self.value = value


@pytest.mark.parametrize(
    "name, value, expected",
    [
        ("x-header", "test", Header("x-header", "test")),
        ("host", "www.example.com", Host("www.example.com")),
    ],
)
def test_header_create_subclass(name: str, value: str, expected: Header):
    header = Header.create(name, value)
    assert header == expected


def test_eq_not():
    h1 = Header("Foo", "bar")
    h2 = XFoo("bar")
    assert h1 != h2


def test_hash():
    assert isinstance(hash(Header("Foo", "bar")), int)
