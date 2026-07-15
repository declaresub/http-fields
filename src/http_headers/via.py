"""Via header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110.via import ViaElement, ViaVisitor


@dataclass(frozen=True)
class Via(Header):
    """Via header, as defined by RFC 9110: the intermediaries a message passed through."""

    name: ClassVar[str] = "Via"
    rule: ClassVar[Rule] = rfc9110.Rule("Via")
    visitor: ClassVar[ViaVisitor] = ViaVisitor()

    elements: tuple[ViaElement, ...]

    def __init__(self, *elements: ViaElement) -> None:
        object.__setattr__(self, "elements", tuple(elements))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(element) for element in self.elements)
