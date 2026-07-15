from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["ForwardedElement", "ForwardedVisitor"]


@dataclass(frozen=True)
class ForwardedElement:
    """One Forwarded element (RFC 7239): an ordered sequence of ``(parameter, value)`` pairs,
    e.g. ``(("for", "192.0.2.60"), ("proto", "http"))``."""

    pairs: tuple[tuple[str, str], ...]

    def __str__(self) -> str:
        return ";".join(f"{key}={val}" for key, val in self.pairs)


class ForwardedVisitor(NodeVisitor):
    @staticmethod
    def visit_forwarded_pair(node: Node) -> tuple[str, str]:
        # forwarded-pair = token "=" value
        return (node.children[0].value, node.children[-1].value)

    def visit_forwarded_element(self, node: Node) -> ForwardedElement:
        pairs = [x for x in map(self.visit, node.children) if isinstance(x, tuple)]
        return ForwardedElement(tuple(pairs))

    def visit_forwarded(self, node: Node) -> list[ForwardedElement]:
        return [
            x for x in map(self.visit, node.children) if isinstance(x, ForwardedElement)
        ]
