"""Structured Field Values for HTTP (RFC 9651).

Provides the value model (``Item``, ``InnerList``, ``Token``, ``DisplayString``) plus parse and
serialize functions for the three top-level types: Item, List, and Dictionary. Bare items map to
native Python types: Integer -> int, Decimal -> decimal.Decimal, String -> str, Token -> Token,
Boolean -> bool, Byte Sequence -> bytes, Date -> datetime, Display String -> DisplayString.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from abnf import NodeVisitor
from abnf.grammars import rfc9651
from abnf.parser import Node

__all__ = [
    "BareItem",
    "DisplayString",
    "InnerList",
    "Item",
    "Member",
    "Parameters",
    "Token",
    "parse_dictionary",
    "parse_item",
    "parse_list",
    "serialize_dictionary",
    "serialize_item",
    "serialize_list",
]


class Token(str):
    """A Structured Fields Token (an unquoted identifier), distinct from a String."""

    __slots__ = ()


class DisplayString(str):
    """A Structured Fields Display String (Unicode text), distinct from a String."""

    __slots__ = ()


# A bare item is one of these Python types (Token/DisplayString are str subclasses).
BareItem = "int | Decimal | bool | bytes | datetime | str | Token | DisplayString"
Parameters = "tuple[tuple[str, object], ...]"


@dataclass(frozen=True)
class Item:
    """A bare item together with its parameters."""

    value: object
    parameters: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True)
class InnerList:
    """An ordered list of items, with parameters, i.e. ``(a b);q=1``."""

    items: tuple[Item, ...] = ()
    parameters: tuple[tuple[str, object], ...] = field(default_factory=tuple)


# A member of a List or Dictionary is either an Item or an InnerList.
Member = "Item | InnerList"


# --- string / display-string / byte helpers -------------------------------------------------


def _unescape_string(raw: str) -> str:
    inner = raw[1:-1]  # strip the surrounding DQUOTEs
    out: list[str] = []
    i = 0
    while i < len(inner):
        if inner[i] == "\\":
            out.append(inner[i + 1])
            i += 2
        else:
            out.append(inner[i])
            i += 1
    return "".join(out)


def _escape_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _decode_displaystring(raw: str) -> DisplayString:
    inner = raw[2:-1]  # strip the leading %" and trailing "
    buf = bytearray()
    i = 0
    while i < len(inner):
        if inner[i] == "%":
            buf.append(int(inner[i + 1 : i + 3], 16))
            i += 3
        else:
            buf.append(ord(inner[i]))
            i += 1
    return DisplayString(buf.decode("utf-8"))


def _encode_displaystring(value: str) -> str:
    out = ['%"']
    for byte in value.encode("utf-8"):
        if byte in (0x25, 0x22) or byte < 0x20 or byte > 0x7E:
            out.append(f"%{byte:02x}")
        else:
            out.append(chr(byte))
    out.append('"')
    return "".join(out)


def _serialize_decimal(value: Decimal) -> str:
    text = f"{value:.3f}".rstrip("0")
    return text + "0" if text.endswith(".") else text


# --- parsing --------------------------------------------------------------------------------


class _StructuredFieldsVisitor(NodeVisitor):
    @staticmethod
    def visit_sf_integer(node: Node) -> int:
        return int(node.value)

    @staticmethod
    def visit_sf_decimal(node: Node) -> Decimal:
        return Decimal(node.value)

    @staticmethod
    def visit_sf_string(node: Node) -> str:
        return _unescape_string(node.value)

    @staticmethod
    def visit_sf_token(node: Node) -> Token:
        return Token(node.value)

    @staticmethod
    def visit_sf_boolean(node: Node) -> bool:
        return node.value == "?1"

    @staticmethod
    def visit_sf_binary(node: Node) -> bytes:
        return base64.b64decode(node.value.strip(":"))

    @staticmethod
    def visit_sf_date(node: Node) -> datetime:
        return datetime.fromtimestamp(int(node.value.lstrip("@")), tz=timezone.utc)

    @staticmethod
    def visit_sf_displaystring(node: Node) -> DisplayString:
        return _decode_displaystring(node.value)

    def visit_bare_item(self, node: Node) -> object:
        return self.visit(node.children[0])

    def visit_param_value(self, node: Node) -> object:
        return self.visit(node.children[0])

    def visit_parameter(self, node: Node) -> tuple[str, object]:
        key = ""
        value: object = True  # a bare parameter key means Boolean true
        for child in node.children:
            if child.name == "param-key":
                key = child.value
            elif child.name == "param-value":
                value = self.visit(child)
        return (key, value)

    def visit_parameters(self, node: Node) -> tuple[tuple[str, object], ...]:
        return tuple(self.visit(c) for c in node.children if c.name == "parameter")

    def visit_sf_item(self, node: Node) -> Item:
        value: object = None
        params: tuple[tuple[str, object], ...] = ()
        for child in node.children:
            if child.name == "bare-item":
                value = self.visit(child)
            elif child.name == "parameters":
                params = self.visit(child)
        return Item(value, params)

    def visit_inner_list(self, node: Node) -> InnerList:
        items = tuple(self.visit(c) for c in node.children if c.name == "sf-item")
        params: tuple[tuple[str, object], ...] = ()
        for child in node.children:
            if child.name == "parameters":
                params = self.visit(child)
        return InnerList(items, params)

    def visit_list_member(self, node: Node) -> object:
        return self.visit(node.children[0])

    def visit_sf_list(self, node: Node) -> tuple[object, ...]:
        return tuple(self.visit(c) for c in node.children if c.name == "list-member")

    def visit_member_value(self, node: Node) -> object:
        return self.visit(node.children[0])

    def visit_dict_member(self, node: Node) -> tuple[str, object]:
        key = ""
        member: object = None
        params: tuple[tuple[str, object], ...] = ()
        for child in node.children:
            if child.name == "member-key":
                key = child.value
            elif child.name == "member-value":
                member = self.visit(child)
            elif child.name == "parameters":
                params = self.visit(child)
        if member is None:
            member = Item(True, params)  # a bare key means Boolean true
        return (key, member)

    def visit_sf_dictionary(self, node: Node) -> tuple[tuple[str, object], ...]:
        return tuple(self.visit(c) for c in node.children if c.name == "dict-member")


_VISITOR = _StructuredFieldsVisitor()


def parse_item(value: str) -> Item:
    """Parse a Structured Fields Item."""
    return _VISITOR.visit(rfc9651.Rule("sf-item").parse_all(value))


def parse_list(value: str) -> tuple[Item | InnerList, ...]:
    """Parse a Structured Fields List into a tuple of Item / InnerList. An empty string is an
    empty list."""
    if not value.strip():
        return ()
    return _VISITOR.visit(rfc9651.Rule("sf-list").parse_all(value))


def parse_dictionary(value: str) -> tuple[tuple[str, Item | InnerList], ...]:
    """Parse a Structured Fields Dictionary into a tuple of (key, Item / InnerList) pairs
    (ordered). An empty string is an empty dictionary."""
    if not value.strip():
        return ()
    return _VISITOR.visit(rfc9651.Rule("sf-dictionary").parse_all(value))


# --- serializing ----------------------------------------------------------------------------


def serialize_bare(value: object) -> str:
    """Serialize a bare item to its Structured Fields text form."""
    if isinstance(value, bool):
        return "?1" if value else "?0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        return _serialize_decimal(value)
    if isinstance(value, DisplayString):
        return _encode_displaystring(value)
    if isinstance(value, Token):
        return str(value)
    if isinstance(value, str):
        return '"' + _escape_string(value) + '"'
    if isinstance(value, bytes):
        return ":" + base64.b64encode(value).decode("ascii") + ":"
    if isinstance(value, datetime):
        return "@" + str(int(value.timestamp()))
    raise TypeError(f"Cannot serialize {value!r} as a Structured Fields bare item.")


def _serialize_params(params: tuple[tuple[str, object], ...]) -> str:
    out: list[str] = []
    for key, value in params:
        out.append(f";{key}" if value is True else f";{key}={serialize_bare(value)}")
    return "".join(out)


def serialize_item(item: Item) -> str:
    """Serialize an Item."""
    return serialize_bare(item.value) + _serialize_params(item.parameters)


def _serialize_inner_list(inner: InnerList) -> str:
    body = " ".join(serialize_item(i) for i in inner.items)
    return f"({body})" + _serialize_params(inner.parameters)


def _serialize_member(member: object) -> str:
    if isinstance(member, InnerList):
        return _serialize_inner_list(member)
    assert isinstance(member, Item)
    return serialize_item(member)


def serialize_list(members: tuple[object, ...]) -> str:
    """Serialize a List of Item / InnerList members."""
    return ", ".join(_serialize_member(m) for m in members)


def serialize_dictionary(members: tuple[tuple[str, object], ...]) -> str:
    """Serialize a Dictionary of (key, Item / InnerList) members."""
    parts: list[str] = []
    for key, member in members:
        if isinstance(member, Item) and member.value is True:
            parts.append(key + _serialize_params(member.parameters))
        else:
            parts.append(f"{key}={_serialize_member(member)}")
    return ", ".join(parts)
