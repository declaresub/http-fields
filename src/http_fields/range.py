"""Range header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.visitors.rfc9110 import RangeUnit
from http_fields.visitors.rfc9110.range import IntRange, RangeVisitor, SuffixRange


@dataclass(frozen=True)
class Range(Header):
    """Range header, as defined by RFC 9110, e.g. ``bytes=0-499,-500``."""

    name: ClassVar[str] = "Range"
    rule: ClassVar[Rule] = rfc9110.Rule("Range")
    visitor: ClassVar[RangeVisitor] = RangeVisitor()

    range_unit: RangeUnit
    ranges: tuple[IntRange | SuffixRange, ...]

    def __init__(self, range_unit: str, *ranges: IntRange | SuffixRange) -> None:
        object.__setattr__(self, "range_unit", RangeUnit(range_unit))
        object.__setattr__(self, "ranges", tuple(ranges))

    @classmethod
    def parse(cls, value: str) -> Self:
        range_unit, ranges = cls.visitor.visit(cls._node(value))
        return cls(range_unit, *ranges)

    @property
    def value(self) -> str:
        return f"{self.range_unit}={','.join(str(r) for r in self.ranges)}"
