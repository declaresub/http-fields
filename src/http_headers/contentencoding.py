"""ContentEncoding header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from abnf.parser import Node, NodeVisitor
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import Token


class ContentEncodingVisitor(NodeVisitor):
    def visit_content_encoding(self, node: Node) -> list[str]:
        return list(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_content_coding(node: Node) -> str:
        return node.value


@dataclass(frozen=True, slots=True)
class ContentEncoding(Header):
    """Content-Encoding header, as defined by RFC 9110."""

    name: ClassVar[str] = "content-encoding"
    rule: ClassVar[Rule] = rfc9110.Rule("Content-Encoding")
    visitor: ClassVar[ContentEncodingVisitor] = ContentEncodingVisitor()

    codings: tuple[Token, ...]

    def __init__(self, *codings: str) -> None:
        object.__setattr__(self, "codings", tuple(Token(c) for c in codings))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(self.codings)
