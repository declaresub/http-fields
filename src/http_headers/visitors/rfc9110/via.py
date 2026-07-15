from dataclasses import dataclass

from abnf import Node, NodeVisitor

__all__ = ["ViaElement", "ViaVisitor"]


@dataclass(frozen=True)
class ViaElement:
    """One hop in a Via header: a received-protocol, a received-by, and an optional comment."""

    received_protocol: str
    received_by: str
    comment: str | None = None

    def __str__(self) -> str:
        text = f"{self.received_protocol} {self.received_by}"
        if self.comment:
            text += f" {self.comment}"
        return text


class ViaVisitor(NodeVisitor):
    def visit_via(self, node: Node) -> list[ViaElement]:
        # the Via node is a flat sequence; each element starts at a received-protocol.
        elements: list[ViaElement] = []
        proto: str | None = None
        by: str = ""
        comment: str | None = None
        for child in node.children:
            if child.name == "received-protocol":
                if proto is not None:
                    elements.append(ViaElement(proto, by, comment))
                proto, by, comment = child.value, "", None
            elif child.name == "received-by":
                by = child.value
            elif child.name == "comment":
                comment = child.value
        if proto is not None:
            elements.append(ViaElement(proto, by, comment))
        return elements
