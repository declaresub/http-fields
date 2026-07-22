"""Base class for headers that are a list of products and comments."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import NodeVisitor
from typing_extensions import Self

from http_fields.header import Header
from http_fields.visitors.rfc9110 import Comment, Product


@dataclass(frozen=True)
class ProductListHeader(Header):
    """Base for headers that are a whitespace-separated list of Product/Comment items
    (User-Agent, Server). Concrete subclasses supply ``name``/``rule``/``visitor``."""

    visitor: ClassVar[NodeVisitor]

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
