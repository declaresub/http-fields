"""Security: bound parse() input length to prevent super-linear-time DoS."""

import pytest

from http_fields import Accept, CacheStatus, Cookie, Host, SetCookie


def test_parse_rejects_oversized_value():
    # A grammar-VALID but very large value must be rejected on length, before the
    # (super-linear) grammar parse runs.
    huge_but_valid = ", ".join("text/html" for _ in range(1000))  # ~13 KB
    assert len(huge_but_valid) > Accept.max_length
    with pytest.raises(ValueError):
        Accept.parse(huge_but_valid)


@pytest.mark.parametrize("cls", [Accept, CacheStatus, Cookie, SetCookie, Host])
def test_parse_rejects_oversized_generic(cls):
    with pytest.raises(ValueError):
        cls.parse("a" * (cls.max_length + 1))


def test_max_length_is_overridable_per_class():
    class BigAccept(Accept):
        max_length = 100_000

    huge_but_valid = ", ".join("text/html" for _ in range(1000))
    # the subclass with a larger cap accepts what the base rejects
    assert BigAccept.parse(huge_but_valid).accept_types
