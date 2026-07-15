import pytest

from http_headers import Header, MaxForwards, NonNegativeInt


def test_maxforwards_parse():
    header = MaxForwards.parse("10")
    assert header.forwards == 10
    assert isinstance(header.forwards, NonNegativeInt)


def test_maxforwards_from_int():
    assert MaxForwards(0).value == "0"


def test_maxforwards_negative():
    with pytest.raises(ValueError):
        MaxForwards(-1)


def test_maxforwards_create():
    assert isinstance(Header.create("max-forwards", "3"), MaxForwards)
