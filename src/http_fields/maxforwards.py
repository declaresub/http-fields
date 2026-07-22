"""Max-Forwards header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import NonNegativeInt


@dataclass(frozen=True)
class MaxForwards(Header):
    """Max-Forwards header, as defined by RFC 9110."""

    name: ClassVar[str] = "Max-Forwards"
    rule: ClassVar[Rule] = rfc9110.Rule("Max-Forwards")

    forwards: NonNegativeInt

    def __init__(self, forwards: int) -> None:
        object.__setattr__(self, "forwards", NonNegativeInt(forwards))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(NonNegativeInt(cls._node(value).value))

    @property
    def value(self) -> str:
        return str(self.forwards)
