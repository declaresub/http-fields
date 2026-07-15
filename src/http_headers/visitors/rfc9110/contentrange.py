from dataclasses import dataclass
from typing import Literal

from abnf import Node, NodeVisitor

from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9110.rangeunit import RangeUnit, RangeUnitVisitor


@dataclass
class RangeResp:
    first_pos: NonNegativeInt
    last_pos: NonNegativeInt
    complete_length: NonNegativeInt | None


@dataclass
class UnsatisfiedRange:
    complete_length: NonNegativeInt | None


class ContentRangeVisitor(NodeVisitor):
    visit_range_unit = RangeUnitVisitor()

    @staticmethod
    def visit_literal(node: Node):
        return "*" if node.value == "*" else None

    @staticmethod
    def visit_complete_length(node: Node):
        return NonNegativeInt(node.value)

    def visit_unsatisfied_range(self, node: Node) -> UnsatisfiedRange:
        item = next(x for x in map(self.visit, node.children) if x is not None)
        return UnsatisfiedRange(item if isinstance(item, NonNegativeInt) else None)

    @staticmethod
    def visit_first_pos(node: Node):
        return NonNegativeInt(node.value)

    @staticmethod
    def visit_last_pos(node: Node):
        return NonNegativeInt(node.value)

    def visit_incl_range(self, node: Node):
        first_pos: NonNegativeInt
        last_pos: NonNegativeInt
        first_pos, last_pos = (
            x for x in map(self.visit, node.children) if x is not None
        )
        return (first_pos, last_pos)

    def visit_range_resp(self, node: Node):
        incl_range: tuple[NonNegativeInt, NonNegativeInt]
        complete_length: NonNegativeInt | Literal["*"]
        incl_range, complete_length = (
            x for x in map(self.visit, node.children) if x is not None
        )
        return RangeResp(
            *incl_range,
            complete_length=complete_length
            if isinstance(complete_length, NonNegativeInt)
            else None,
        )

    def visit_content_range(self, node: Node):
        range_unit: RangeUnit
        range: RangeResp | UnsatisfiedRange
        range_unit, range = (x for x in map(self.visit, node.children) if x is not None)
        return range_unit, range
