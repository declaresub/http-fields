from collections.abc import Iterable
from dataclasses import dataclass

from abnf import Node, NodeVisitor

import http_fields.visitors.rfc9110.quotedstring as quotedstring
import http_fields.visitors.rfc9110.token as token

__all__ = [
    "Param",
    "ParamsInput",
    "Parameter",
    "ParameterVisitor",
    "ParametersVisitor",
    "as_params",
    "param_from_node",
    "parsed_param",
    "value_leaf",
]


Token = token.Token
TokenVisitor = token.TokenVisitor
QuotedString = quotedstring.QuotedString
QuotedStringVisitor = quotedstring.QuotedStringVisitor


def value_leaf(value: str) -> "Token | QuotedString":
    """Coerce a parameter value to the right self-validating leaf: a Token if it is one,
    otherwise a (double-quoted, escaped) QuotedString. An existing leaf passes through."""
    try:
        return Token(value)
    except ValueError:
        return QuotedString(value)


@dataclass(frozen=True)
class Parameter:
    name: Token
    value: Token | QuotedString

    def __init__(self, name: str, value: str):
        object.__setattr__(self, "name", Token(name))
        object.__setattr__(self, "value", value_leaf(value))

    def __str__(self):
        return f"{self.name}={self.value}"


@dataclass(frozen=True)
class Param:
    """A generic ``name`` or ``name=value`` parameter: a token name with an optional
    token / quoted-string value. Used by headers (Link, Prefer, Alt-Svc, ...) whose
    parameters may be valueless. Self-validating: an invalid name or value cannot be built."""

    name: Token
    value: Token | QuotedString | None = None

    def __init__(self, name: str, value: str | None = None) -> None:
        object.__setattr__(self, "name", Token(name))
        object.__setattr__(
            self, "value", value_leaf(value) if value is not None else None
        )

    def __str__(self) -> str:
        return str(self.name) if self.value is None else f"{self.name}={self.value}"


# What a value object's constructor accepts for its params: ready-made Param objects
# or raw ``(name[, value])`` tuples (coerced by as_params).
ParamsInput = Iterable[Param | tuple[str, ...]]


def as_params(items: ParamsInput) -> tuple[Param, ...]:
    """Coerce an iterable of ``Param`` (kept as-is) or raw ``(name[, value])`` tuples into a
    tuple of validated ``Param``. Lets value-object constructors accept either form."""
    return tuple(p if isinstance(p, Param) else Param(*p) for p in items)


def parsed_param(name: str, value: str | None) -> Param:
    """Build a ``Param`` from already-parsed node text, wrapping the parts as leaves with
    ``parse=False`` so the parse() path does not re-parse (QuotedString still validates)."""
    if value is None:
        return Param(Token(name, parse=False))
    leaf = QuotedString(value) if value[:1] == '"' else Token(value, parse=False)
    return Param(Token(name, parse=False), leaf)


def param_from_node(node: Node) -> Param:
    """Build a ``Param`` from a ``token [ "=" ( token / quoted-string ) ]`` node (the shape
    shared by Link-, Prefer-, and Alt-Svc-style parameters)."""
    name = node.children[0].value
    value: str | None = None
    seen_eq = False
    for child in node.children[1:]:
        if child.name == "literal" and child.value == "=":
            seen_eq = True
        elif seen_eq and child.name not in ("BWS", "OWS"):
            value = child.value
    return parsed_param(name, value)


class ParameterVisitor(NodeVisitor):
    visit_quoted_string = QuotedStringVisitor()
    visit_token = TokenVisitor()

    def visit_parameter(self, node: Node):
        name: Token
        value: Token | QuotedString
        name, value = filter(None, map(self.visit, node.children))
        return Parameter(name, value)

    def visit_parameter_name(self, node: Node) -> Token:
        return next(filter(None, map(self.visit, node.children)))

    def visit_parameter_value(self, node: Node) -> Token | QuotedString:
        return next(filter(None, map(self.visit, node.children)))


class ParametersVisitor(NodeVisitor):
    visit_parameter = ParameterVisitor()

    def visit_parameters(self, node: Node) -> list[Parameter]:
        return list(filter(None, map(self.visit, node.children)))
