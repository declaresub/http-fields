"""Origin header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import cors
from typing_extensions import Self

from http_headers.header import Header
from http_headers.parsedobjs import ParsedStr


class OriginValue(ParsedStr):
    """An Origin value (``scheme://host[:port]`` or ``null``). Self-validating."""

    parser = cors.Rule("Origin")


@dataclass(frozen=True)
class Origin(Header):
    """Origin header, as defined by RFC 6454 / the Fetch standard.

    The origin (``scheme://host[:port]`` or ``null``) is validated on construction.
    """

    name: ClassVar[str] = "origin"
    rule: ClassVar[Rule] = cors.Rule("Origin")

    origin: OriginValue

    def __init__(self, origin: str) -> None:
        # The origin self-validates as a leaf; build from a string via Origin(...).
        object.__setattr__(self, "origin", OriginValue(origin))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    @property
    def value(self) -> str:
        return self.origin
