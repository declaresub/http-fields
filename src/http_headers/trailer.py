"""Trailer header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Node, NodeVisitor, Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import FieldName


class TrailerVisitor(NodeVisitor):
    def visit_trailer(self, node: Node) -> list[str]:
        return [x for x in map(self.visit, node.children) if x is not None]

    @staticmethod
    def visit_field_name(node: Node) -> str:
        return node.value


@dataclass(frozen=True)
class Trailer(Header):
    """Trailer header, as defined by RFC 9110."""

    name: ClassVar[str] = "Trailer"
    rule: ClassVar[Rule] = rfc9110.Rule("Trailer")
    visitor: ClassVar[TrailerVisitor] = TrailerVisitor()

    field_names: tuple[FieldName, ...]

    def __init__(self, *field_names: FieldName) -> None:
        object.__setattr__(self, "field_names", tuple(field_names))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(
            *(FieldName(f, parse=False) for f in cls.visitor.visit(cls._node(value)))
        )

    @property
    def value(self) -> str:
        return ", ".join(self.field_names)
