from dataclasses import FrozenInstanceError

import pytest

from http_headers import Accept
from http_headers.accept import AcceptType


def test_accept_parse():
    accept = Accept.parse("*/*")
    assert accept.accept_types == (AcceptType(type="*", subtype="*"),)


def test_accept_value():
    accept = Accept(AcceptType(type="*", subtype="*"))
    assert accept.value == "*/*"


def test_accept_empty():
    assert Accept().value == ""


def test_accept_quoted_q_is_parameter():
    # A quoted "q" is a media-range parameter, not a weight, and must not crash
    # (regression: bug 15).
    accept = Accept.parse('text/html;q="0.5"')
    assert accept.accept_types[0].weight is None
    assert Accept.parse(accept.value) == accept


def test_accept_out_of_range_q_not_clamped():
    # q=5 is not a valid qvalue; keep it as a parameter rather than clamp to 1.
    accept = Accept.parse("text/html;q=5")
    assert accept.accept_types[0].weight is None
    assert Accept.parse(accept.value) == accept


def test_accepttype_is_frozen():
    at = AcceptType(type="text", subtype="html")
    with pytest.raises(FrozenInstanceError):
        at.weight = None  # type: ignore[misc]
    assert at == AcceptType(type="text", subtype="html")
    assert repr(at) == (
        "AcceptType(type=Token('text'), subtype=Token('html'), params=(), weight=None)"
    )
