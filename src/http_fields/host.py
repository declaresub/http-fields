"""Host header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import NonNegativeInt
from http_fields.visitors.rfc9110 import Hostname, HostVisitor


@dataclass(frozen=True)
class Host(Header):
    """Host header, as defined by RFC 9110.

    Host: www.example.com
    """

    name: ClassVar[str] = "host"
    rule: ClassVar[Rule] = rfc9110.Rule("Host")
    visitor: ClassVar[HostVisitor] = HostVisitor()

    hostname: Hostname
    port: NonNegativeInt | None = None

    def __init__(self, hostname: str, port: int | None = None) -> None:
        # hostname/port self-validate as leaves (an already-parsed value passes through),
        # so a valid uri-host and numeric port serialize to a valid Host -- no re-parse.
        object.__setattr__(self, "hostname", Hostname(hostname))
        object.__setattr__(
            self, "port", NonNegativeInt(port) if port is not None else None
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        hostname, port = cls.visitor.visit(cls._node(value))
        return cls(hostname, port)

    @property
    def value(self) -> str:
        return self.hostname + (f":{self.port}" if self.port is not None else "")
