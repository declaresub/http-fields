from dataclasses import dataclass

from abnf import Node, NodeVisitor

from http_headers.visitors.rfc9110.parameters import (
    Param,
    ParamsInput,
    QuotedString,
    Token,
    as_params,
    param_from_node,
    parsed_param,
    value_leaf,
)

__all__ = ["Preference", "PreferVisitor", "PreferenceAppliedVisitor"]


@dataclass(frozen=True)
class Preference:
    """One RFC 7240 preference: a token, an optional value, and optional parameters.
    Self-validating: an invalid name, value, or parameter cannot be built."""

    name: Token
    value: Token | QuotedString | None = None
    parameters: tuple[Param, ...] = ()

    def __init__(
        self,
        name: str,
        value: str | None = None,
        parameters: ParamsInput = (),
    ) -> None:
        object.__setattr__(self, "name", Token(name))
        object.__setattr__(
            self, "value", value_leaf(value) if value is not None else None
        )
        object.__setattr__(self, "parameters", as_params(parameters))

    def __str__(self) -> str:
        out = str(self.name) if self.value is None else f"{self.name}={self.value}"
        for p in self.parameters:
            out += f"; {p}"
        return out


class PreferVisitor(NodeVisitor):
    def visit_preference(self, node: Node) -> Preference:
        # token [ "=" word ] *( ";" parameter )
        name = node.children[0].value
        value: str | None = None
        params: list[Param] = []
        seen_eq = False
        for child in node.children[1:]:
            if child.name == "parameter":
                params.append(param_from_node(child))
            elif child.name == "literal" and child.value == "=" and not params:
                seen_eq = True
            elif seen_eq and value is None and child.name not in ("BWS", "OWS"):
                value = child.value
        # Build the head (name + optional value) trusted, then hand its leaves to
        # Preference, whose coercion passes them through unchanged.
        head = parsed_param(name, value)
        return Preference(head.name, head.value, params)

    def visit_prefer(self, node: Node) -> list[Preference]:
        return [
            self.visit_preference(c) for c in node.children if c.name == "preference"
        ]


class PreferenceAppliedVisitor(PreferVisitor):
    # RFC 7240's abnf uses the same `preference` production for Preference-Applied.
    def visit_preference_applied(self, node: Node) -> list[Preference]:
        return [
            self.visit_preference(c) for c in node.children if c.name == "preference"
        ]
