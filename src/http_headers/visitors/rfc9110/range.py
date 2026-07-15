from dataclasses import dataclass

from abnf import Node, NodeVisitor

from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9110.rangeunit import RangeUnit

__all__ = ["IntRange", "RangeVisitor", "SuffixRange"]


@dataclass(frozen=True)
class IntRange:
    """An RFC 9110 int-range, e.g. ``0-499`` or ``500-`` (open-ended)."""

    first_pos: NonNegativeInt
    last_pos: NonNegativeInt | None = None

    def __init__(self, first_pos: int, last_pos: int | None = None) -> None:
        object.__setattr__(self, "first_pos", NonNegativeInt(first_pos))
        object.__setattr__(
            self, "last_pos", None if last_pos is None else NonNegativeInt(last_pos)
        )

    def __str__(self) -> str:
        last = "" if self.last_pos is None else str(self.last_pos)
        return f"{self.first_pos}-{last}"


@dataclass(frozen=True)
class SuffixRange:
    """An RFC 9110 suffix-range, e.g. ``-500`` (the final N units)."""

    suffix_length: NonNegativeInt

    def __init__(self, suffix_length: int) -> None:
        object.__setattr__(self, "suffix_length", NonNegativeInt(suffix_length))

    def __str__(self) -> str:
        return f"-{self.suffix_length}"


class RangeVisitor(NodeVisitor):
    @staticmethod
    def visit_range_unit(node: Node) -> RangeUnit:
        return RangeUnit(node.value, parse=False)

    @staticmethod
    def visit_first_pos(node: Node) -> NonNegativeInt:
        return NonNegativeInt(node.value)

    @staticmethod
    def visit_last_pos(node: Node) -> NonNegativeInt:
        return NonNegativeInt(node.value)

    @staticmethod
    def visit_suffix_length(node: Node) -> NonNegativeInt:
        return NonNegativeInt(node.value)

    def visit_int_range(self, node: Node) -> IntRange:
        items = [x for x in map(self.visit, node.children) if x is not None]
        return IntRange(items[0], items[1] if len(items) == 2 else None)

    def visit_suffix_range(self, node: Node) -> SuffixRange:
        items = [x for x in map(self.visit, node.children) if x is not None]
        return SuffixRange(items[0])

    def visit_range_spec(self, node: Node) -> IntRange | SuffixRange:
        return next(filter(None, map(self.visit, node.children)))

    def visit_range_set(self, node: Node) -> list[IntRange | SuffixRange]:
        return [
            x
            for x in map(self.visit, node.children)
            if isinstance(x, (IntRange, SuffixRange))
        ]

    def visit_ranges_specifier(
        self, node: Node
    ) -> tuple[RangeUnit, list[IntRange | SuffixRange]]:
        range_unit = RangeUnit("bytes", parse=False)
        ranges: list[IntRange | SuffixRange] = []
        for child in node.children:
            result = self.visit(child)
            if isinstance(result, RangeUnit):
                range_unit = result
            elif isinstance(result, list):
                ranges = result
        return (range_unit, ranges)

    def visit_range(self, node: Node) -> tuple[RangeUnit, list[IntRange | SuffixRange]]:
        return next(filter(None, map(self.visit, node.children)))
