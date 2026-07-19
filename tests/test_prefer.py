from http_headers import Header, Prefer, PreferenceApplied
from http_headers.visitors.rfc7240 import Preference


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


def test_prefer_create():
    assert isinstance(Header.create("prefer", "respond-async"), Prefer)
    assert isinstance(
        Header.create("preference-applied", "return=representation"), PreferenceApplied
    )
