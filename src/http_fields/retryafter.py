"""Retry-After header class."""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import NonNegativeInt
from http_fields.visitors.rfc9110 import RetryAfterVisitor, imf_fixdate


@dataclass(frozen=True)
class RetryAfter(Header):
    """Retry-After header, as defined by RFC 9110. The delay is either a number of seconds
    (a NonNegativeInt) or an HTTP-date."""

    name: ClassVar[str] = "Retry-After"
    rule: ClassVar[Rule] = rfc9110.Rule("Retry-After")
    visitor: ClassVar[RetryAfterVisitor] = RetryAfterVisitor()

    delay: NonNegativeInt | datetime

    def __init__(self, delay: int | datetime) -> None:
        if isinstance(delay, datetime):
            object.__setattr__(self, "delay", delay)
        # Runtime guard against callers that ignore the type annotation; the int check
        # reads as redundant to the type checker but rejects a stray non-int at runtime.
        elif isinstance(delay, int) and not isinstance(delay, bool):  # pyright: ignore[reportUnnecessaryIsInstance]
            object.__setattr__(self, "delay", NonNegativeInt(delay))
        else:
            raise TypeError("delay must be an int or datetime.")

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        if isinstance(self.delay, datetime):
            return imf_fixdate(self.delay)
        return str(self.delay)
