"""Origin header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import cors
from typing_extensions import Self

from http_headers.header import Header


@dataclass(frozen=True)
class Origin(Header):
    """Origin header, as defined by RFC 6454 / the Fetch standard.

    The origin (``scheme://host[:port]`` or ``null``) is validated and stored as a string.
    """

    name: ClassVar[str] = "origin"
    rule: ClassVar[Rule] = cors.Rule("Origin")

    origin: str

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls._node(value).value)

    @property
    def value(self) -> str:
        return self.origin
