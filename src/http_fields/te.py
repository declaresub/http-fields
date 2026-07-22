"""TE header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.visitors.rfc9110.te import TCoding, TEVisitor


@dataclass(frozen=True)
class TE(Header):
    """TE header, as defined by RFC 9110: the transfer-codings the client is willing to
    accept (plus the special ``trailers`` token), each with an optional weight."""

    name: ClassVar[str] = "TE"
    rule: ClassVar[Rule] = rfc9110.Rule("TE")
    visitor: ClassVar[TEVisitor] = TEVisitor()

    codings: tuple[TCoding, ...]

    def __init__(self, *codings: TCoding) -> None:
        # Each TCoding self-validates (Token coding, safe Weight/Parameter), so the
        # field-type check fully guarantees a safe serialized value -- no re-parse.
        object.__setattr__(self, "codings", tuple(codings))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(coding) for coding in self.codings)
