"""Forwarded header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc7239
from typing_extensions import Self

from http_fields.header import Header
from http_fields.visitors.rfc7239 import ForwardedElement, ForwardedVisitor


@dataclass(frozen=True)
class Forwarded(Header):
    """Forwarded header, as defined by RFC 7239 (the standardized replacement for the de-facto
    ``X-Forwarded-*`` headers)."""

    name: ClassVar[str] = "Forwarded"
    rule: ClassVar[Rule] = rfc7239.Rule("Forwarded")
    visitor: ClassVar[ForwardedVisitor] = ForwardedVisitor()

    elements: tuple[ForwardedElement, ...]

    def __init__(self, *elements: ForwardedElement) -> None:
        # Each ForwardedElement self-validates (Param pairs), so the field-type check
        # fully guarantees a safe serialized value -- no re-parse.
        object.__setattr__(self, "elements", tuple(elements))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(element) for element in self.elements)
