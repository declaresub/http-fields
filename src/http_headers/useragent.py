"""User-Agent header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import Comment, Product, UserAgentVisitor


@dataclass(frozen=True)
class UserAgent(Header):
    """User-Agent header, as defined by RFC 9110. ``items`` is a sequence of Product or
    Comment values."""

    name: ClassVar[str] = "User-Agent"
    rule: ClassVar[Rule] = rfc9110.Rule("User-Agent")
    visitor: ClassVar[UserAgentVisitor] = UserAgentVisitor()

    items: tuple[Product | Comment, ...]

    def __init__(self, *items: Product | Comment) -> None:
        object.__setattr__(self, "items", tuple(items))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        # the grammar requires at least one SP/TAB between items, so a source with multiple
        # spaces between items is not reassembled identically.
        return " ".join(str(item) for item in self.items)
