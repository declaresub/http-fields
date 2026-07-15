import pytest

from http_headers import Vary


def test_from_value():
    value = "accept-encoding, accept-language"
    header = Vary(value)
    assert header.field_names == ["accept-encoding", "accept-language"]


def test_from_field_names():
    field_names = ["accept-encoding, accept-language"]
    header = Vary(field_names=field_names)
    assert header.value == "accept-encoding, accept-language"


def test_star_value():
    assert Vary().value == "*"


def test_invalid_field_name():
    with pytest.raises(ValueError):
        Vary(field_names=["test:"])


def test_invalid_value():
    with pytest.raises(ValueError):
        Vary("test\n")
