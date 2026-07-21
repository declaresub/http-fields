from dataclasses import dataclass

from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_headers.parsedobjs import ParsedStr

__all__ = ["Comment", "ReceivedBy", "ReceivedProtocol", "ViaElement", "ViaVisitor"]


class ReceivedProtocol(ParsedStr):
    """An RFC 9110 received-protocol (e.g. ``HTTP/1.1``). Self-validating."""

    parser = rfc9110.Rule("received-protocol")


class ReceivedBy(ParsedStr):
    """An RFC 9110 received-by (a host[:port] or pseudonym). Self-validating."""

    parser = rfc9110.Rule("received-by")


class Comment(ParsedStr):
    """An RFC 9110 comment, including its enclosing parentheses. Self-validating."""

    parser = rfc9110.Rule("comment")


@dataclass(frozen=True)
class ViaElement:
    """One hop in a Via header: a received-protocol, a received-by, and an optional comment."""

    received_protocol: ReceivedProtocol
    received_by: ReceivedBy
    comment: Comment | None = None

    def __init__(
        self,
        received_protocol: str,
        received_by: str,
        comment: str | None = None,
    ) -> None:
        # Each field self-validates as a leaf; an existing leaf passes through unchanged.
        object.__setattr__(
            self, "received_protocol", ReceivedProtocol(received_protocol)
        )
        object.__setattr__(self, "received_by", ReceivedBy(received_by))
        object.__setattr__(
            self, "comment", Comment(comment) if comment is not None else None
        )

    def __str__(self) -> str:
        text = f"{self.received_protocol} {self.received_by}"
        if self.comment:
            text += f" {self.comment}"
        return text


def _element(proto: str, by: str, comment: str | None) -> ViaElement:
    # Build from already-validated node text (parse=False), so construction does not re-parse.
    return ViaElement(
        ReceivedProtocol(proto, parse=False),
        ReceivedBy(by, parse=False),
        Comment(comment, parse=False) if comment is not None else None,
    )


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
                    elements.append(_element(proto, by, comment))
                proto, by, comment = child.value, "", None
            elif child.name == "received-by":
                by = child.value
            elif child.name == "comment":
                comment = child.value
        if proto is not None:
            elements.append(_element(proto, by, comment))
        return elements
