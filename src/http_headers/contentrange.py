"""Content-Range header class"""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9110 import ContentRangeVisitor, RangeUnit
from http_headers.visitors.rfc9110.contentrange import RangeResp, UnsatisfiedRange


class ContentRange(Header):
    name = "content-range"
    visitor = ContentRangeVisitor()

    def __init__(
        self,
        value: str | None = None,
        *,
        range_unit: str | None = None,
        first_pos: int | None = None,
        last_pos: int | None = None,
        complete_length: int | None = None,
    ):
        if isinstance(value, str):
            self.value = value
        else:
            if not isinstance(range_unit, str):
                raise TypeError("range_unit must be a str if value is None.")
            self.range_unit = RangeUnit(range_unit)
            if (first_pos is None) != (last_pos is None):
                raise ValueError(
                    "Both first_pos and last_pos must be non-negative ints, or both None."
                )
            if first_pos is None and last_pos is None and complete_length is None:
                raise ValueError(
                    "complete_length must be a non-negative int if first_pos, last_pos are both None."
                )

            self.first_pos = (
                NonNegativeInt(first_pos) if first_pos is not None else None
            )
            self.last_pos = NonNegativeInt(last_pos) if last_pos is not None else None
            self.complete_length = (
                NonNegativeInt(complete_length) if complete_length is not None else None
            )

    @property
    def value(self):
        if self.first_pos and self.first_pos:
            return f"{self.range_unit} {self.first_pos}-{self.last_pos}/{self.complete_length if self.complete_length else '*'}"
        else:
            return f"{self.range_unit} */{self.complete_length}"

    @value.setter
    def value(self, val: str):
        node = rfc9110.Rule("Content-Range").parse_all(val)
        range_unit: RangeUnit
        range: RangeResp | UnsatisfiedRange
        range_unit, range = self.visitor.visit(node)
        self.range_unit = range_unit
        self.first_pos = range.first_pos if isinstance(range, RangeResp) else None
        self.last_pos = range.last_pos if isinstance(range, RangeResp) else None
        self.complete_length = range.complete_length
