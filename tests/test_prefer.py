import pytest

from http_fields import Header, Prefer, PreferenceApplied
from http_fields.visitors.rfc7240 import Preference


def test_prefer_parse():
    header = Prefer.parse("respond-async, wait=10")
    assert header.preferences == (
        Preference("respond-async"),
        Preference("wait", "10"),
    )


def test_prefer_value():
    header = Prefer(Preference("return", "representation"), Preference("respond-async"))
    assert header.value == "return=representation, respond-async"


def test_preference_applied_parse():
    header = PreferenceApplied.parse("return=representation")
    assert header.preferences == (Preference("return", "representation"),)


def test_preference_applied_parse_multiple():
    header = PreferenceApplied.parse("return=minimal, respond-async")
    assert header.preferences == (
        Preference("return", "minimal"),
        Preference("respond-async"),
    )


@pytest.mark.parametrize("value", ["respond-async; wait=10", "return=minimal; x"])
def test_preference_applied_rejects_parameters(value: str):
    # RFC 7240 section 3: applied-pref carries no parameters, unlike Prefer's preference.
    with pytest.raises(ValueError):
        PreferenceApplied.parse(value)


def test_prefer_create():
    assert isinstance(Header.create("prefer", "respond-async"), Prefer)
    assert isinstance(
        Header.create("preference-applied", "return=representation"), PreferenceApplied
    )
