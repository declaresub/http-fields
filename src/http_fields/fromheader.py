"""From header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import ParsedStr


class Mailbox(ParsedStr):
    """A From-header mailbox (RFC 9110 / RFC 5322 addr-spec). Self-validating."""

    parser = rfc9110.Rule("From")


@dataclass(frozen=True)
class From(Header):
    """From header, as defined by RFC 9110: the mailbox of the user controlling the client.

    The mailbox is validated against RFC 9110 (RFC 5322 addr-spec) on construction.
    """

    name: ClassVar[str] = "From"
    rule: ClassVar[Rule] = rfc9110.Rule("From")

    mailbox: Mailbox

    def __init__(self, mailbox: str) -> None:
        # The mailbox self-validates as a leaf; build from a string via From(...).
        object.__setattr__(self, "mailbox", Mailbox(mailbox))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    @property
    def value(self) -> str:
        return self.mailbox
