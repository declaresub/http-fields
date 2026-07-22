"""Accept header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.visitors.rfc9110 import AcceptType, AcceptVisitor


@dataclass(frozen=True)
class Accept(Header):
    """Accept header, as defined by RFC 9110.

    An Accept header may have an empty value (``Accept:``), which is treated as accepting
    any media type. RFC 9110 no longer includes ext-params (accept-ext) in the grammar.
    """

    name: ClassVar[str] = "Accept"
    rule: ClassVar[Rule] = rfc9110.Rule("Accept")
    visitor: ClassVar[AcceptVisitor] = AcceptVisitor()

    accept_types: tuple[AcceptType, ...]

    def __init__(self, *accept_types: AcceptType) -> None:
        object.__setattr__(self, "accept_types", tuple(accept_types))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(accept_type) for accept_type in self.accept_types)
