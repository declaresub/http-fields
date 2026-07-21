import pytest

from http_headers import Age, NonNegativeInt


def test_age_parse():
    header = Age.parse("111")
    assert header.seconds == 111


def test_age_from_init():
    header = Age(NonNegativeInt(111))
    assert isinstance(header.seconds, NonNegativeInt)
    assert header.seconds == 111


def test_age_init_coerces_int():
    header = Age(111)
    assert isinstance(header.seconds, NonNegativeInt)
    assert header.seconds == 111


def test_age_value():
    assert Age(NonNegativeInt(111)).value == "111"


def test_age_str():
    assert str(Age(111)) == "age: 111"


def test_age_negative():
    with pytest.raises(ValueError):
        Age(-5)


def test_age_eq_and_hash():
    assert Age(111) == Age(111)
    assert hash(Age(111)) == hash(Age(111))
    assert Age(111) != Age(112)


def test_age_rejects_non_integral_float():
    # A non-integral float must be rejected, not silently truncated (bug 24).
    with pytest.raises(ValueError):
        Age(3.7)  # type: ignore[arg-type]
