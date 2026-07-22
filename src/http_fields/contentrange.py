"""Content-Range header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import NonNegativeInt
from http_fields.visitors.rfc9110 import ContentRangeVisitor, RangeUnit
from http_fields.visitors.rfc9110.contentrange import RangeResp


@dataclass(frozen=True)
class ContentRange(Header):
    """Content-Range header, as defined by RFC 9110."""

    name: ClassVar[str] = "content-range"
    rule: ClassVar[Rule] = rfc9110.Rule("Content-Range")
    visitor: ClassVar[ContentRangeVisitor] = ContentRangeVisitor()

    range_unit: RangeUnit
    first_pos: NonNegativeInt | None
    last_pos: NonNegativeInt | None
    complete_length: NonNegativeInt | None

    def __init__(
        self,
        range_unit: str,
        *,
        first_pos: int | None = None,
        last_pos: int | None = None,
        complete_length: int | None = None,
    ) -> None:
        if (first_pos is None) != (last_pos is None):
            raise ValueError(
                "Both first_pos and last_pos must be given, or both omitted."
            )
        if first_pos is None and complete_length is None:
            raise ValueError(
                "complete_length is required when first_pos and last_pos are omitted."
            )
        object.__setattr__(self, "range_unit", RangeUnit(range_unit))
        object.__setattr__(
            self, "first_pos", None if first_pos is None else NonNegativeInt(first_pos)
        )
        object.__setattr__(
            self, "last_pos", None if last_pos is None else NonNegativeInt(last_pos)
        )
        object.__setattr__(
            self,
            "complete_length",
            None if complete_length is None else NonNegativeInt(complete_length),
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        range_unit, rng = cls.visitor.visit(cls._node(value))
        satisfied = isinstance(rng, RangeResp)
        return cls(
            range_unit,
            first_pos=rng.first_pos if satisfied else None,
            last_pos=rng.last_pos if satisfied else None,
            complete_length=rng.complete_length,
        )

    @property
    def value(self) -> str:
        if self.first_pos is not None and self.last_pos is not None:
            length = self.complete_length if self.complete_length is not None else "*"
            return f"{self.range_unit} {self.first_pos}-{self.last_pos}/{length}"
        return f"{self.range_unit} */{self.complete_length}"
