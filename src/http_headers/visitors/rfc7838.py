from collections.abc import Iterable
from dataclasses import dataclass

from abnf import Node, NodeVisitor
from abnf.grammars import rfc7838

from http_headers.parsedobjs import ParsedStr
from http_headers.visitors.rfc9110.parameters import Param, as_params, parsed_param

__all__ = ["AltAuthority", "AltSvcVisitor", "AltValue", "ProtocolId"]


class ProtocolId(ParsedStr):
    """An RFC 7838 protocol-id (a percent-encoded ALPN protocol name). Self-validating."""

    parser = rfc7838.Rule("protocol-id")


class AltAuthority(ParsedStr):
    """An RFC 7838 alt-authority: a quoted ``host:port`` (the enclosing quotes are part of
    the value). Self-validating."""

    parser = rfc7838.Rule("alt-authority")


def _pair(node: Node) -> tuple[str, str | None]:
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
class AltValue:
    """One RFC 7838 alt-value: a protocol-id, an alt-authority, and parameters."""

    protocol_id: ProtocolId
    authority: AltAuthority
    params: tuple[Param, ...] = ()

    def __init__(
        self,
        protocol_id: str,
        authority: str,
        params: "Iterable[Param | tuple[str, ...]]" = (),
    ) -> None:
        # Each part self-validates; an existing leaf/Param passes through unchanged.
        object.__setattr__(self, "protocol_id", ProtocolId(protocol_id))
        object.__setattr__(self, "authority", AltAuthority(authority))
        object.__setattr__(self, "params", as_params(params))

    def __str__(self) -> str:
        out = f"{self.protocol_id}={self.authority}"
        for p in self.params:
            out += f"; {p}"
        return out


class AltSvcVisitor(NodeVisitor):
    @staticmethod
    def visit_alternative(node: Node) -> tuple[str, str]:
        # protocol-id "=" alt-authority
        return (node.children[0].value, node.children[-1].value)

    def visit_alt_value(self, node: Node) -> AltValue:
        protocol_id = authority = ""
        params: list[Param] = []
        for child in node.children:
            if child.name == "alternative":
                protocol_id, authority = self.visit_alternative(child)
            elif child.name == "parameter":
                params.append(parsed_param(*_pair(child)))
        return AltValue(
            ProtocolId(protocol_id, parse=False),
            AltAuthority(authority, parse=False),
            params,
        )

    def visit_alt_svc(self, node: Node) -> list[AltValue]:
        return [self.visit_alt_value(c) for c in node.children if c.name == "alt-value"]
