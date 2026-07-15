"""Expect header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Node, NodeVisitor, Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header


class ExpectVisitor(NodeVisitor):
    @staticmethod
    def visit_expectation(node: Node) -> str:
        return node.value

    def visit_expect(self, node: Node) -> list[str]:
        return [x for x in map(self.visit, node.children) if x is not None]


@dataclass(frozen=True)
class Expect(Header):
    """Expect header, as defined by RFC 9110 (in practice almost always ``100-continue``)."""

    name: ClassVar[str] = "Expect"
    rule: ClassVar[Rule] = rfc9110.Rule("Expect")
    visitor: ClassVar[ExpectVisitor] = ExpectVisitor()

    expectations: tuple[str, ...]

    def __init__(self, *expectations: str) -> None:
        object.__setattr__(self, "expectations", tuple(expectations))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(self.expectations)
