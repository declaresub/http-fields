"""Connection header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import ConnectionVisitor, Token


@dataclass(frozen=True, slots=True)
class Connection(Header):
    """Connection header, as defined by RFC 9110."""

    name: ClassVar[str] = "connection"
    rule: ClassVar[Rule] = rfc9110.Rule("Connection")
    visitor: ClassVar[ConnectionVisitor] = ConnectionVisitor()

    directives: tuple[Token, ...]

    def __init__(self, *directives: str) -> None:
        object.__setattr__(self, "directives", tuple(Token(d) for d in directives))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ",".join(self.directives)
