from dataclasses import dataclass

from abnf import Node, NodeVisitor
from abnf.grammars import rfc9110

from http_headers.parsedobjs import ParsedStr

__all__ = ["Protocol", "ProtocolName", "ProtocolVersion", "UpgradeVisitor"]


class ProtocolName(ParsedStr):
    """An RFC 9110 protocol-name token. Self-validating."""

    parser = rfc9110.Rule("protocol-name")


class ProtocolVersion(ParsedStr):
    """An RFC 9110 protocol-version token. Self-validating."""

    parser = rfc9110.Rule("protocol-version")


@dataclass(frozen=True)
class Protocol:
    """An RFC 9110 protocol: a name with an optional version, e.g. ``HTTP/2``."""

    name: ProtocolName
    version: ProtocolVersion | None = None

    def __init__(self, name: str, version: str | None = None) -> None:
        # Coerce str -> leaf (which validates); an existing leaf passes through
        # unchanged, so a value from the visitor is not re-parsed.
        object.__setattr__(self, "name", ProtocolName(name))
        object.__setattr__(
            self, "version", ProtocolVersion(version) if version is not None else None
        )

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
        version = ProtocolVersion(items[1], parse=False) if len(items) == 2 else None
        return Protocol(ProtocolName(items[0], parse=False), version)

    def visit_upgrade(self, node: Node) -> list[Protocol]:
        return [x for x in map(self.visit, node.children) if isinstance(x, Protocol)]
