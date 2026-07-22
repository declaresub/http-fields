"""If-Range header class."""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from abnf import Node, NodeVisitor, Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.visitors.rfc9110 import EntityTag, HttpDateVisitor, imf_fixdate
from http_fields.visitors.rfc9110.entitytag import EntityTagVisitor


class IfRangeVisitor(NodeVisitor):
    visit_entity_tag = EntityTagVisitor()
    visit_http_date = HttpDateVisitor()

    def visit_if_range(self, node: Node) -> EntityTag | datetime:
        return next(filter(None, map(self.visit, node.children)))


@dataclass(frozen=True)
class IfRange(Header):
    """If-Range header, as defined by RFC 9110. The condition is an entity-tag or an
    HTTP-date."""

    name: ClassVar[str] = "If-Range"
    rule: ClassVar[Rule] = rfc9110.Rule("If-Range")
    visitor: ClassVar[IfRangeVisitor] = IfRangeVisitor()

    condition: EntityTag | datetime

    def __init__(self, condition: EntityTag | datetime) -> None:
        # Runtime guard for callers that ignore the type annotation.
        if not isinstance(condition, (EntityTag, datetime)):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("condition must be an EntityTag or datetime.")
        object.__setattr__(self, "condition", condition)

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        if isinstance(self.condition, datetime):
            return imf_fixdate(self.condition)
        return str(self.condition)
