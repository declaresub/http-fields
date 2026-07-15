"""Accept-Encoding header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AcceptEncodingVisitor, Weight, WeightedCoding


@dataclass(frozen=True)
class AcceptEncoding(Header):
    """Accept-Encoding header, as defined by RFC 9110."""

    name: ClassVar[str] = "accept-encoding"
    rule: ClassVar[Rule] = rfc9110.Rule("Accept-Encoding")
    visitor: ClassVar[AcceptEncodingVisitor] = AcceptEncodingVisitor()

    codings: tuple[WeightedCoding, ...]

    def __init__(
        self, *codings: WeightedCoding | tuple[str, float | Weight | None]
    ) -> None:
        object.__setattr__(
            self,
            "codings",
            tuple(
                c if isinstance(c, WeightedCoding) else WeightedCoding(*c)
                for c in codings
            ),
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(coding) for coding in self.codings)
