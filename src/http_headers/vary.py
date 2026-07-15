"""Vary header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc7231
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import FieldName, VaryVisitor


@dataclass(frozen=True)
class Vary(Header):
    """Vary header, as defined by RFC 9110.

    An empty ``field_names`` serializes as ``*`` (vary by anything).

    Vary: accept-encoding, accept-language
    """

    name: ClassVar[str] = "Vary"
    rule: ClassVar[Rule] = rfc7231.Rule("Vary")
    visitor: ClassVar[VaryVisitor] = VaryVisitor()

    field_names: tuple[FieldName, ...]

    def __init__(self, *field_names: str) -> None:
        object.__setattr__(
            self, "field_names", tuple(FieldName(f) for f in field_names)
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(self.field_names) if self.field_names else "*"
