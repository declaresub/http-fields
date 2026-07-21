"""Upgrade header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110.upgrade import Protocol, UpgradeVisitor


@dataclass(frozen=True)
class Upgrade(Header):
    """Upgrade header, as defined by RFC 9110: a list of protocols, e.g. ``HTTP/2, WebSocket``."""

    name: ClassVar[str] = "Upgrade"
    rule: ClassVar[Rule] = rfc9110.Rule("Upgrade")
    visitor: ClassVar[UpgradeVisitor] = UpgradeVisitor()

    protocols: tuple[Protocol, ...]

    def __init__(self, *protocols: Protocol) -> None:
        object.__setattr__(self, "protocols", tuple(protocols))
        if protocols:
            self._validate_value()

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(protocol) for protocol in self.protocols)
