"""Age header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9111
from typing_extensions import Self

from http_headers.header import Header
from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9111 import AgeVisitor


@dataclass(frozen=True, slots=True)
class Age(Header):
    """Age header, as defined by RFC 9111."""

    name: ClassVar[str] = "age"
    rule: ClassVar[Rule] = rfc9111.Rule("Age")
    visitor: ClassVar[AgeVisitor] = AgeVisitor()

    seconds: NonNegativeInt

    def __init__(self, seconds: int) -> None:
        object.__setattr__(self, "seconds", NonNegativeInt(seconds))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return str(self.seconds)
