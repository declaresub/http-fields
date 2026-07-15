"""From header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header


@dataclass(frozen=True)
class From(Header):
    """From header, as defined by RFC 9110: the mailbox of the user controlling the client.

    The mailbox is validated against RFC 9110 (RFC 5322 addr-spec) and stored as a string.
    """

    name: ClassVar[str] = "From"
    rule: ClassVar[Rule] = rfc9110.Rule("From")

    mailbox: str

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls._node(value).value)

    @property
    def value(self) -> str:
        return self.mailbox
