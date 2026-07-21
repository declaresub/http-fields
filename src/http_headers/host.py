"""Host header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.parsedobjs import CaselessMixin
from http_headers.visitors.rfc9110 import HostVisitor


class _HostName(CaselessMixin, str):
    """Host names compare case-insensitively (RFC 9110 / RFC 3986 host)."""

    __slots__ = ()


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

    def __post_init__(self) -> None:
        # Compare host names case-insensitively while preserving the original text.
        if not isinstance(self.hostname, _HostName):
            object.__setattr__(self, "hostname", _HostName(self.hostname))
        # Reject invalid input (including CR/LF/NUL injection) at construction.
        self._validate_value()

    @classmethod
    def parse(cls, value: str) -> Self:
        hostname, port = cls.visitor.visit(cls._node(value))
        return cls(hostname, port)

    @property
    def value(self) -> str:
        return self.hostname + (f":{self.port}" if self.port is not None else "")
