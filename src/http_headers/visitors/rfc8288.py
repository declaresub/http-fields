from collections.abc import Iterable
from dataclasses import dataclass

from abnf import Node, NodeVisitor
from abnf.grammars import rfc8288

from http_headers.parsedobjs import ParsedStr
from http_headers.visitors.rfc9110.parameters import Param, as_params, parsed_param

__all__ = ["LinkValue", "LinkVisitor", "URIReference"]


class URIReference(ParsedStr):
    """An RFC 3986 URI-Reference, as used by RFC 8288's link target. Self-validating."""

    parser = rfc8288.Rule("URI-Reference")


def _pair(node: Node) -> tuple[str, str | None]:
    """Extract a ``token [ "=" ( token / quoted-string ) ]`` node as ``(name, value)``."""
    name = node.children[0].value
    value: str | None = None
    seen_eq = False
    for child in node.children[1:]:
        if child.name == "literal" and child.value == "=":
            seen_eq = True
        elif seen_eq and child.name not in ("BWS", "OWS"):
            value = child.value
    return (name, value)


@dataclass(frozen=True)
class LinkValue:
    """One RFC 8288 link-value: a target URI reference plus link-params."""

    target: URIReference
    params: tuple[Param, ...] = ()

    def __init__(
        self, target: str, params: "Iterable[Param | tuple[str, ...]]" = ()
    ) -> None:
        # target and each Param self-validate; an existing leaf/Param passes through.
        object.__setattr__(self, "target", URIReference(target))
        object.__setattr__(self, "params", as_params(params))

    def __str__(self) -> str:
        out = f"<{self.target}>"
        for p in self.params:
            out += f"; {p}"
        return out


class LinkVisitor(NodeVisitor):
    def visit_link_value(self, node: Node) -> LinkValue:
        target = ""
        params: list[Param] = []
        for child in node.children:
            if child.name == "URI-Reference":
                target = child.value
            elif child.name == "link-param":
                params.append(parsed_param(*_pair(child)))
        return LinkValue(URIReference(target, parse=False), params)

    def visit_link(self, node: Node) -> list[LinkValue]:
        return [
            self.visit_link_value(c) for c in node.children if c.name == "link-value"
        ]
