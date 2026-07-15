import pytest

from http_headers import EntityTag, IfNoneMatch


@pytest.mark.parametrize(
    "value, expected",
    [
        ("*", IfNoneMatch("*")),
        ('"deadbeef"', IfNoneMatch(EntityTag("deadbeef"))),
        ('"deadbeef"', IfNoneMatch([EntityTag("deadbeef")])),
    ],
)
def test_ifnonematch_from_value(value: str, expected: IfNoneMatch):
    assert IfNoneMatch(value) == expected


def test_ifnonematch_matches():
    header = IfNoneMatch([EntityTag("deadbeef"), EntityTag("test")])
    assert header.matches(EntityTag("foo"))


def test_ifnonematch_matches_none():
    header = IfNoneMatch("*")
    assert not header.matches(EntityTag("test"))
