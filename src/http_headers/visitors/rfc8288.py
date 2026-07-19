from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["LinkValue", "LinkVisitor"]


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

    target: str
    params: tuple[tuple[str, str | None], ...] = ()

    def __str__(self) -> str:
        out = f"<{self.target}>"
        for name, value in self.params:
            out += f"; {name}" if value is None else f"; {name}={value}"
        return out


class LinkVisitor(NodeVisitor):
    def visit_link_value(self, node: Node) -> LinkValue:
        target = ""
        params: list[tuple[str, str | None]] = []
        for child in node.children:
            if child.name == "URI-Reference":
                target = child.value
            elif child.name == "link-param":
                params.append(_pair(child))
        return LinkValue(target, tuple(params))

    def visit_link(self, node: Node) -> list[LinkValue]:
        return [
            self.visit_link_value(c) for c in node.children if c.name == "link-value"
        ]
