"""Expect header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Node, NodeVisitor, Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.parsedobjs import ParsedStr


class Expectation(ParsedStr):
    """An RFC 9110 expectation (e.g. ``100-continue``). Self-validating."""

    parser = rfc9110.Rule("expectation")


class ExpectVisitor(NodeVisitor):
    @staticmethod
    def visit_expectation(node: Node) -> Expectation:
        # The node is already parsed; skip re-validation.
        return Expectation(node.value, parse=False)

    def visit_expect(self, node: Node) -> list[Expectation]:
        return [x for x in map(self.visit, node.children) if x is not None]


@dataclass(frozen=True)
class Expect(Header):
    """Expect header, as defined by RFC 9110 (in practice almost always ``100-continue``)."""

    name: ClassVar[str] = "Expect"
    rule: ClassVar[Rule] = rfc9110.Rule("Expect")
    visitor: ClassVar[ExpectVisitor] = ExpectVisitor()

    expectations: tuple[Expectation, ...]

    def __init__(self, *expectations: Expectation) -> None:
        # Store already-parsed Expectation values (each validated itself on creation).
        # The base runtime check enforces the field type; build from a string with
        # Expect.parse().
        object.__setattr__(self, "expectations", tuple(expectations))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(self.expectations)
