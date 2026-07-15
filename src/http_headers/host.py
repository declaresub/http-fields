"""Host header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import HostVisitor


@dataclass(frozen=True)
class Host(Header):
    """Host header, as defined by RFC 9110.

    Host: www.example.com
    """

    name: ClassVar[str] = "host"
    rule: ClassVar[Rule] = rfc9110.Rule("Host")
    visitor: ClassVar[HostVisitor] = HostVisitor()

    hostname: str
    port: int | None = None

    @classmethod
    def parse(cls, value: str) -> Self:
        hostname, port = cls.visitor.visit(cls._node(value))
        return cls(hostname, port)

    @property
    def value(self) -> str:
        return self.hostname + (f":{self.port}" if self.port else "")
