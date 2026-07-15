"""Allow header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AllowVisitor, Token


@dataclass(frozen=True)
class Allow(Header):
    """Allow header, as defined by RFC 9110.

    Allow: GET, POST, OPTIONS
    """

    name: ClassVar[str] = "Allow"
    rule: ClassVar[Rule] = rfc9110.Rule("Allow")
    visitor: ClassVar[AllowVisitor] = AllowVisitor()

    methods: tuple[Token, ...]

    def __init__(self, *methods: str) -> None:
        object.__setattr__(self, "methods", tuple(Token(m) for m in methods))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ",".join(self.methods)
