from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["Protocol", "UpgradeVisitor"]


@dataclass(frozen=True)
class Protocol:
    """An RFC 9110 protocol: a name with an optional version, e.g. ``HTTP/2``."""

    name: str
    version: str | None = None

    def __str__(self) -> str:
        return self.name + (f"/{self.version}" if self.version else "")


class UpgradeVisitor(NodeVisitor):
    @staticmethod
    def visit_protocol_name(node: Node) -> str:
        return node.value

    @staticmethod
    def visit_protocol_version(node: Node) -> str:
        return node.value

    def visit_protocol(self, node: Node) -> Protocol:
        items = [x for x in map(self.visit, node.children) if x is not None]
        return Protocol(items[0], items[1] if len(items) == 2 else None)

    def visit_upgrade(self, node: Node) -> list[Protocol]:
        return [x for x in map(self.visit, node.children) if isinstance(x, Protocol)]
