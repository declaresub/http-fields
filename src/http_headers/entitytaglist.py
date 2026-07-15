"""Base class for headers that are a list of entity-tags or ``*``."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import NodeVisitor
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import EntityTag


@dataclass(frozen=True)
class EntityTagListHeader(Header):
    """Base for If-Match / If-None-Match: a list of entity-tags, or ``*`` (``wildcard``).

    Concrete subclasses supply ``name``/``rule``/``visitor`` (the visitor returns either the
    string ``"*"`` or a list of :class:`EntityTag`) and their own ``matches()`` semantics.
    """

    visitor: ClassVar[NodeVisitor]

    entity_tags: tuple[EntityTag, ...]
    wildcard: bool

    def __init__(self, *entity_tags: EntityTag, wildcard: bool = False) -> None:
        object.__setattr__(self, "entity_tags", tuple(entity_tags))
        object.__setattr__(self, "wildcard", wildcard)

    @classmethod
    def parse(cls, value: str) -> Self:
        result = cls.visitor.visit(cls._node(value))
        if result == "*":
            return cls(wildcard=True)
        return cls(*result)

    @property
    def value(self) -> str:
        return "*" if self.wildcard else ", ".join(str(t) for t in self.entity_tags)
