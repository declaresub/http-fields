"""Regression tests for the 'plausible' review findings (P1-P6)."""

import warnings
from datetime import datetime

import pytest

from http_headers import ContentType, Date, UserAgent
from http_headers.structuredfields import BareItem, InnerList, Item, Member
from http_headers.visitors.rfc9110._base import imf_fixdate, transform
from http_headers.visitors.rfc9110.comment import Comment


def test_p1_type_aliases_are_real_types():
    # BareItem / Member are usable types, not strings (regression: P1).
    assert not isinstance(BareItem, str)
    assert not isinstance(Member, str)
    assert isinstance(5, BareItem)
    assert isinstance("x", BareItem)
    assert isinstance(Item(1), Member)
    assert isinstance(InnerList(), Member)


def test_p2_contenttype_charset_unquoted():
    # A quoted charset parameter is exposed without its DQUOTEs (regression: P2).
    assert ContentType.parse('text/html; charset="utf-8"').charset == "utf-8"
    assert ContentType.parse("text/html; charset=utf-8").charset == "utf-8"


def test_p2_contenttype_boundary_unquoted():
    ct = ContentType.parse('multipart/form-data; boundary="a b"')
    assert ct.boundary == "a b"


def test_p3_comment_is_immutable_and_stably_hashed():
    # Comment.items is a tuple, so it can't be mutated and its hash is stable
    # (regression: P3).
    ua = UserAgent.parse("foo (bar)")
    before = hash(ua)
    comment = next(item for item in ua.items if isinstance(item, Comment))
    assert isinstance(comment.items, tuple)
    with pytest.raises(AttributeError):
        comment.items.append("baz")  # type: ignore[attr-defined]
    assert hash(ua) == before


def test_comment_is_frozen():
    # Comment is a frozen dataclass, so the attribute cannot be rebound (which
    # would otherwise change its hash after use as a set/dict key).
    from dataclasses import FrozenInstanceError

    c = Comment("a", "b")
    with pytest.raises(FrozenInstanceError):
        c.items = ("hacked",)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        c.injected = 1  # type: ignore[attr-defined]
    assert c == Comment("a", "b")
    assert repr(c) == "Comment(items=('a', 'b'))"


def test_p4_rfc850_date_no_deprecation_warning():
    # Parsing a 2-digit-year date must not use the deprecated datetime.utcnow()
    # (regression: P4).
    with warnings.catch_warnings():
        warnings.filterwarnings("error", message=".*utcnow.*")
        Date.parse("Sunday, 06-Nov-94 08:49:37 GMT")


def test_p5_transform_correctness():
    assert list(transform(iter([1, 2, 3]), int, str)) == [
        (1, None),
        (2, None),
        (3, None),
    ]
    assert list(transform(iter([1, "a", 2]), int, str)) == [(1, "a"), (2, None)]


def test_p5_transform_handles_long_input_without_recursion():
    # Previously recursive: a long stream exceeded the recursion limit
    # (regression: P5).
    n = 10_000
    result = list(transform(iter(range(n)), int, str))
    assert len(result) == n
    assert result[-1] == (n - 1, None)


def test_p6_imf_fixdate_year_zero_padded():
    # Years < 1000 must serialize as 4 digits per the fixdate grammar (regression: P6).
    assert imf_fixdate(datetime(42, 1, 1, 0, 0, 0)) == "Wed, 01 Jan 0042 00:00:00 GMT"


def test_comment_parses_str_content_to_structure():
    # A str arg is parsed as comment content; embedded (...) become nested
    # Comment objects (construction == parse).
    c = Comment("foo (bar) baz")
    assert c == Comment("foo ", Comment("bar"), " baz")
    parsed = next(
        i for i in UserAgent.parse("x (foo (bar) baz)").items if isinstance(i, Comment)
    )
    assert c == parsed


def test_comment_escaped_paren_in_str():
    c = Comment(r"a\)b")  # escaped -> literal ) in a text run
    assert c.items == ("a)b",)
    assert str(c) == r"(a\)b)"


@pytest.mark.parametrize("bad", ["a\r\nb", "a)b", "a(b"])
def test_comment_rejects_invalid_str(bad: str):
    with pytest.raises(ValueError):
        Comment(bad)
