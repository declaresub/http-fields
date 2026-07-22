"""ContentLength header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import NonNegativeInt
from http_fields.visitors.rfc9110 import ContentLengthVisitor


@dataclass(frozen=True)
class ContentLength(Header):
    """Content-Length header."""

    name: ClassVar[str] = "content-length"
    rule: ClassVar[Rule] = rfc9110.Rule("Content-Length")
    visitor: ClassVar[ContentLengthVisitor] = ContentLengthVisitor()

    length: NonNegativeInt

    def __init__(self, length: int) -> None:
        object.__setattr__(self, "length", NonNegativeInt(length))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return str(self.length)
