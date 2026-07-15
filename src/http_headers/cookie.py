"""Cookie header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc6265
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc6265 import CookiePair, CookieStringVisitor


@dataclass(frozen=True)
class Cookie(Header):
    """Cookie header, as defined by RFC 6265."""

    name: ClassVar[str] = "Cookie"
    rule: ClassVar[Rule] = rfc6265.Rule("cookie-string")
    visitor: ClassVar[CookieStringVisitor] = CookieStringVisitor()

    pairs: tuple[CookiePair, ...]

    def __init__(self, *pairs: CookiePair | tuple[str, str]) -> None:
        object.__setattr__(
            self,
            "pairs",
            tuple(p if isinstance(p, CookiePair) else CookiePair(*p) for p in pairs),
        )

    @classmethod
    def parse(cls, value: str) -> Self:
        # cookies are often sent with an invalid trailing semicolon; strip it before parsing.
        return cls(*cls.visitor.visit(cls._node(value.rstrip(";"))))

    @property
    def value(self) -> str:
        return "; ".join(f"{pair.name}={pair.value}" for pair in self.pairs)
