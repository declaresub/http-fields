import pytest

from http_fields import Vary
from http_fields.visitors.rfc9110 import FieldName


def test_vary_parse():
    header = Vary.parse("accept-encoding, accept-language")
    assert header.field_names == ("accept-encoding", "accept-language")


def test_vary_from_field_names():
    header = Vary(FieldName("accept-encoding"), FieldName("accept-language"))
    assert header.value == "accept-encoding, accept-language"


def test_vary_star():
    assert Vary().value == "*"
    assert Vary.parse("*").value == "*"


def test_vary_invalid_field_name():
    with pytest.raises(ValueError):
        Vary(FieldName("test:"))


def test_vary_invalid_value():
    with pytest.raises(ValueError):
        Vary.parse("test\n")
