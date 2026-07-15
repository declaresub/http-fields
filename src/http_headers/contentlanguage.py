"""Content-Language header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110.contentlanguage import (
    ContentLanguageVisitor,
    LanguageTag,
)


@dataclass(frozen=True)
class ContentLanguage(Header):
    """Content-Language header, as defined by RFC 9110."""

    name: ClassVar[str] = "content-language"
    rule: ClassVar[Rule] = rfc9110.Rule("Content-Language")
    visitor: ClassVar[ContentLanguageVisitor] = ContentLanguageVisitor()

    languages: tuple[LanguageTag, ...]

    def __init__(self, *languages: str) -> None:
        object.__setattr__(self, "languages", tuple(LanguageTag(x) for x in languages))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(self.languages)
