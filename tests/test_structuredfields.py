from datetime import datetime, timezone
from decimal import Decimal

import pytest

from http_headers.structuredfields import (
    DisplayString,
    InnerList,
    Item,
    Token,
    parse_dictionary,
    parse_item,
    parse_list,
    serialize_bare,
    serialize_dictionary,
    serialize_item,
    serialize_list,
)


@pytest.mark.parametrize(
    "item",
    [
        Item("café"),  # non-ASCII in a String
        Item("tab\there"),  # control char in a String
        Item(Token("not a token")),  # invalid Token (space)
        Item(10**15),  # integer out of range
        Item(1, (("BAD KEY", 2),)),  # invalid parameter key
    ],
)
def test_serialize_rejects_invalid_items(item: Item):
    # RFC 9651 section 4.1: a serializer must fail on values it cannot represent
    # (regression: bug 12).
    with pytest.raises(ValueError):
        serialize_item(item)


def test_serialize_bare_rejects_out_of_range_int():
    with pytest.raises(ValueError):
        serialize_bare(10**16)


def test_serialize_dictionary_rejects_invalid_key():
    with pytest.raises(ValueError):
        serialize_dictionary((("BAD KEY", Item(1)),))


def test_parameters_duplicate_key_last_wins():
    # RFC 9651: a duplicate key keeps the last value (regression: bug 22).
    assert parse_item("1;a=1;a=2").parameters == (("a", 2),)


def test_dictionary_duplicate_key_last_wins():
    assert parse_dictionary("a=1, a=2") == (("a", Item(2)),)


def test_dictionary_duplicate_preserves_first_position():
    assert parse_dictionary("a=1, b=2, a=3") == (("a", Item(3)), ("b", Item(2)))


def test_serialize_naive_datetime_is_utc():
    # A naive datetime must be interpreted as UTC, not the machine's local tz
    # (regression: bug 24).
    naive = datetime(2021, 1, 1, 0, 0, 0)
    expected = int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp())
    assert serialize_bare(naive) == f"@{expected}"


@pytest.mark.parametrize(
    "text, value",
    [
        ("42", 42),
        ("4.5", Decimal("4.5")),
        ('"hello"', "hello"),
        ("abc", Token("abc")),
        ("?1", True),
        ("?0", False),
        (":aGVsbG8=:", b"hello"),
        ("@1659578233", datetime(2022, 8, 4, 1, 57, 13, tzinfo=timezone.utc)),
        ('%"f%c3%bc%c3%9f"', DisplayString("füß")),
    ],
)
def test_bare_item_types(text: str, value: object):
    item = parse_item(text)
    assert item.value == value
    assert type(item.value) is type(value)
    assert serialize_item(item) == text


def test_token_vs_string_distinct():
    # a Token serializes bare; a String is quoted
    assert serialize_item(Item(Token("abc"))) == "abc"
    assert serialize_item(Item("abc")) == '"abc"'


def test_item_parameters():
    item = parse_item("5;foo=bar;baz")
    assert item.value == 5
    assert item.parameters == (("foo", Token("bar")), ("baz", True))
    assert serialize_item(item) == "5;foo=bar;baz"


def test_string_escaping():
    item = parse_item(r'"a\"b\\c"')
    assert item.value == r'a"b\c'
    assert serialize_item(item) == r'"a\"b\\c"'


def test_list_with_inner_list():
    members = parse_list("sugar, tea, (a b);x=1")
    assert members == (
        Item(Token("sugar")),
        Item(Token("tea")),
        InnerList((Item(Token("a")), Item(Token("b"))), (("x", 1),)),
    )
    assert serialize_list(members) == "sugar, tea, (a b);x=1"


def test_dictionary():
    members = parse_dictionary("a=1, b, c=(1 2);y, d=?0")
    assert members == (
        ("a", Item(1)),
        ("b", Item(True)),
        ("c", InnerList((Item(1), Item(2)), (("y", True),))),
        ("d", Item(False)),
    )
    assert serialize_dictionary(members) == "a=1, b, c=(1 2);y, d=?0"


def test_empty():
    assert parse_list("") == ()
    assert parse_dictionary("  ") == ()
    assert serialize_list(()) == ""
    assert serialize_dictionary(()) == ""
