import pytest

from http_headers import Location


def test_location_from_value():
    value = "https://www.example.com/test"
    location = Location(value)
    assert location.uri == value
    assert location.value == value


@pytest.mark.parametrize(
    "bad",
    [
        "https://ok/\r\nSet-Cookie: sid=attacker",  # CRLF injection
        "https://ok/\nX: y",  # bare LF
        "https://ok/\x00",  # NUL
        "has spaces and stuff",  # not a URI-reference at all
    ],
)
def test_location_constructor_rejects_invalid(bad: str):
    # The natural constructor must validate like parse() does, so a raw string
    # cannot smuggle CR/LF/NUL into the serialized header (security).
    with pytest.raises(ValueError):
        Location(bad)


def test_location_constructor_accepts_valid():
    loc = Location("https://example.com/path")
    assert loc.value == "https://example.com/path"
    assert b"\r" not in bytes(loc) and b"\n" not in bytes(loc)
