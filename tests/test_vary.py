import pytest

from http_headers import Vary


def test_vary_parse():
    header = Vary.parse("accept-encoding, accept-language")
    assert header.field_names == ("accept-encoding", "accept-language")


def test_vary_from_field_names():
    header = Vary("accept-encoding", "accept-language")
    assert header.value == "accept-encoding, accept-language"


def test_vary_star():
    assert Vary().value == "*"
    assert Vary.parse("*").value == "*"


def test_vary_invalid_field_name():
    with pytest.raises(ValueError):
        Vary("test:")


def test_vary_invalid_value():
    with pytest.raises(ValueError):
        Vary.parse("test\n")
