"""Accept-Language header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import (
    AcceptLanguageVisitor,
    Weight,
    WeightedLanguageRange,
)


@dataclass(frozen=True)
class AcceptLanguage(Header):
    """Accept-Language header, as defined by RFC 9110."""

    name: ClassVar[str] = "accept-language"
    rule: ClassVar[Rule] = rfc9110.Rule("Accept-Language")
    visitor: ClassVar[AcceptLanguageVisitor] = AcceptLanguageVisitor()

    language_ranges: tuple[WeightedLanguageRange, ...]

    def __init__(
        self,
        *language_ranges: WeightedLanguageRange | tuple[str, float | Weight | None],
    ) -> None:
        object.__setattr__(
            self,
            "language_ranges",
            tuple(
                r if isinstance(r, WeightedLanguageRange) else WeightedLanguageRange(*r)
                for r in language_ranges
            ),
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(r) for r in self.language_ranges)
