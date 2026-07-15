"""Location header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import LocationVisitor


@dataclass(frozen=True)
class Location(Header):
    """Location header, as defined by RFC 9110."""

    name: ClassVar[str] = "Location"
    rule: ClassVar[Rule] = rfc9110.Rule("Location")
    visitor: ClassVar[LocationVisitor] = LocationVisitor()

    uri: str

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return self.uri
