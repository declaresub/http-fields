import pytest

from http_headers import CustomHeader, Header, Host


def test_customheader_fields():
    header = CustomHeader("X-Test", "example.com")
    assert header.name == "X-Test"
    assert header.value == "example.com"


def test_customheader_invalid_name():
    with pytest.raises(ValueError):
        CustomHeader("X-Header abcd", "test")


def test_customheader_invalid_value():
    with pytest.raises(ValueError):
        CustomHeader("X-Header", "test\rfail")


def test_customheader_str():
    assert str(CustomHeader("Foo", "bar")) == "Foo: bar"


def test_customheader_bytes():
    assert bytes(CustomHeader("Foo", "bar")) == b"Foo: bar"


def test_customheader_asgi_value():
    assert CustomHeader("Foo", "bar").asgi_value == (b"Foo", b"bar")


def test_customheader_hash():
    assert isinstance(hash(CustomHeader("Foo", "bar")), int)


def test_header_create_custom():
    header = Header.create("Foo", "bar")
    assert isinstance(header, CustomHeader)
    assert header.name == "Foo"
    assert header.value == "bar"


@pytest.mark.parametrize(
    "name, value, expected",
    [
        ("x-header", "test", CustomHeader("x-header", "test")),
        ("host", "www.example.com", Host("www.example.com")),
    ],
)
def test_header_create_subclass(name: str, value: str, expected: Header):
    assert Header.create(name, value) == expected


def test_header_eq_distinct_types():
    assert CustomHeader("Foo", "bar") != Host("www.example.com")


def test_asgi_value_uses_latin1():
    # asgi_value must use the class encoding (latin-1), matching __bytes__, not
    # ASCII, so obs-text values don't crash (regression: bug 17).
    header = CustomHeader("X-A", "café")
    name, value = header.asgi_value
    assert name == b"X-A"
    assert value == "café".encode("latin-1")
