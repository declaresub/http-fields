import pytest

from http_headers import EntityTag, IfMatch


@pytest.mark.parametrize(
    "value, expected",
    [
        ("*", IfMatch("*")),
        ('"deadbeef"', IfMatch(EntityTag("deadbeef"))),
        ('"deadbeef"', IfMatch([EntityTag("deadbeef")])),
    ],
)
def test_ifmatch_from_value(value: str, expected: IfMatch):
    assert IfMatch(value) == expected


def test_ifmatch_matches():
    header = IfMatch([EntityTag("deadbeef"), EntityTag("test")])
    assert header.matches(EntityTag("deadbeef"))


def test_ifmatch_matches_any():
    header = IfMatch("*")
    assert header.matches(EntityTag("test"))
