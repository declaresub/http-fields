"""Link header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc8288
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc8288 import LinkValue, LinkVisitor


@dataclass(frozen=True)
class Link(Header):
    """Link header, as defined by RFC 8288 (Web Linking)."""

    name: ClassVar[str] = "Link"
    rule: ClassVar[Rule] = rfc8288.Rule("Link")
    visitor: ClassVar[LinkVisitor] = LinkVisitor()

    links: tuple[LinkValue, ...]

    def __init__(self, *links: LinkValue) -> None:
        object.__setattr__(self, "links", tuple(links))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(link) for link in self.links)
