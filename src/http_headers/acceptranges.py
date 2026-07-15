"""AcceptRanges header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AcceptRangesVisitor, RangeUnit


@dataclass(frozen=True)
class AcceptRanges(Header):
    """Accept-Ranges header, as defined by RFC 9110."""

    name: ClassVar[str] = "accept-ranges"
    rule: ClassVar[Rule] = rfc9110.Rule("accept-ranges")
    visitor: ClassVar[AcceptRangesVisitor] = AcceptRangesVisitor()

    range_units: tuple[RangeUnit, ...]

    def __init__(self, *range_units: str) -> None:
        object.__setattr__(
            self, "range_units", tuple(RangeUnit(r) for r in range_units)
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ",".join(self.range_units)
