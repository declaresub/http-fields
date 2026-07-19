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
    serialize_dictionary,
    serialize_item,
    serialize_list,
)


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
