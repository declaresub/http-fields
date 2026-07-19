from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["Preference", "PreferVisitor", "PreferenceAppliedVisitor"]


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
class Preference:
    """One RFC 7240 preference: a token, an optional value, and optional parameters."""

    name: str
    value: str | None = None
    parameters: tuple[tuple[str, str | None], ...] = ()

    def __str__(self) -> str:
        out = self.name if self.value is None else f"{self.name}={self.value}"
        for name, value in self.parameters:
            out += f"; {name}" if value is None else f"; {name}={value}"
        return out


class PreferVisitor(NodeVisitor):
    def visit_preference(self, node: Node) -> Preference:
        # token [ "=" word ] *( ";" parameter )
        name = node.children[0].value
        value: str | None = None
        params: list[tuple[str, str | None]] = []
        seen_eq = False
        for child in node.children[1:]:
            if child.name == "parameter":
                params.append(_pair(child))
            elif child.name == "literal" and child.value == "=" and not params:
                seen_eq = True
            elif seen_eq and value is None and child.name not in ("BWS", "OWS"):
                value = child.value
        return Preference(name, value, tuple(params))

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
