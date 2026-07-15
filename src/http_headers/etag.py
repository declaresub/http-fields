"""ETag header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import EntityTag, ETagVisitor


@dataclass(frozen=True)
class ETag(Header):
    """ETag header, as defined by RFC 9110."""

    name: ClassVar[str] = "ETag"
    rule: ClassVar[Rule] = rfc9110.Rule("ETag")
    visitor: ClassVar[ETagVisitor] = ETagVisitor()

    entity_tag: EntityTag

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @classmethod
    def from_tag(cls, tag: str, weak: bool = False) -> Self:
        """Build an ETag from an opaque tag and optional weak flag."""
        return cls(EntityTag(tag, weak=weak))

    @property
    def value(self) -> str:
        return str(self.entity_tag)

    def matches(self, entity_tag: EntityTag | None, weak: bool = False) -> bool:
        """Return True if this ETag matches ``entity_tag`` per RFC 9110 comparison.

        Comparison against None is supported and returns False.
        """
        return (
            self.entity_tag.compare(entity_tag, weak=weak)
            if isinstance(entity_tag, EntityTag)
            else False
        )
