"""Accept-Charset header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AcceptCharsetVisitor, Token, Weight


def _as_weight(value: float | Weight | None) -> Weight | None:
    """Normalize a weight argument to a Weight or None. A numeric 0 is a valid weight
    ("not acceptable"), so only None means "no weight specified"."""
    if isinstance(value, Weight):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return Weight(float(value))
    return None


@dataclass(frozen=True)
class AcceptCharset(Header):
    """Accept-Charset header, as defined by RFC 9110."""

    name: ClassVar[str] = "accept-charset"
    rule: ClassVar[Rule] = rfc9110.Rule("Accept-Charset")
    visitor: ClassVar[AcceptCharsetVisitor] = AcceptCharsetVisitor()

    charsets: tuple[tuple[Token, Weight | None], ...]

    def __init__(self, *charsets: tuple[str, float | Weight | None]) -> None:
        object.__setattr__(
            self, "charsets", tuple((Token(c), _as_weight(w)) for c, w in charsets)
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(
            f"{charset}" + (f";{weight}" if weight is not None else "")
            for charset, weight in self.charsets
        )
