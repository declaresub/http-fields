"""Base class for headers whose value is a single HTTP-date."""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from abnf import NodeVisitor
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import imf_fixdate


@dataclass(frozen=True)
class DateHeader(Header):
    """Base for headers whose value is a single HTTP-date (RFC 9110 section 5.6.7).

    Concrete subclasses supply ``name``, ``rule``, and ``visitor`` as ClassVars; the visitor
    must return a :class:`datetime.datetime`.
    """

    visitor: ClassVar[NodeVisitor]

    date: datetime

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return imf_fixdate(self.date)
