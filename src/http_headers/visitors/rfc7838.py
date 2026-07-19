from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["AltValue", "AltSvcVisitor"]


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

    protocol_id: str
    authority: str
    params: tuple[tuple[str, str | None], ...] = ()

    def __str__(self) -> str:
        out = f"{self.protocol_id}={self.authority}"
        for name, value in self.params:
            out += f"; {name}" if value is None else f"; {name}={value}"
        return out


class AltSvcVisitor(NodeVisitor):
    @staticmethod
    def visit_alternative(node: Node) -> tuple[str, str]:
        # protocol-id "=" alt-authority
        return (node.children[0].value, node.children[-1].value)

    def visit_alt_value(self, node: Node) -> AltValue:
        protocol_id = authority = ""
        params: list[tuple[str, str | None]] = []
        for child in node.children:
            if child.name == "alternative":
                protocol_id, authority = self.visit_alternative(child)
            elif child.name == "parameter":
                params.append(_pair(child))
        return AltValue(protocol_id, authority, tuple(params))

    def visit_alt_svc(self, node: Node) -> list[AltValue]:
        return [self.visit_alt_value(c) for c in node.children if c.name == "alt-value"]
