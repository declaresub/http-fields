"""Strict-Transport-Security header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc6797
from typing_extensions import Self

from http_headers.header import Header
from http_headers.parsedobjs import NonNegativeInt


@dataclass(frozen=True)
class StrictTransportSecurity(Header):
    """Strict-Transport-Security (HSTS) header, as defined by RFC 6797."""

    name: ClassVar[str] = "Strict-Transport-Security"
    rule: ClassVar[Rule] = rfc6797.Rule("Strict-Transport-Security")

    max_age: NonNegativeInt
    include_subdomains: bool = False
    preload: bool = False

    def __init__(
        self, max_age: int, include_subdomains: bool = False, preload: bool = False
    ) -> None:
        object.__setattr__(self, "max_age", NonNegativeInt(max_age))
        object.__setattr__(self, "include_subdomains", include_subdomains)
        object.__setattr__(self, "preload", preload)

    @classmethod
    def parse(cls, value: str) -> Self:
        # the grammar rule matches the whole header line, so prepend the field name.
        node = cls._prefixed_node(value)
        max_age = 0
        include_subdomains = False
        preload = False
        for directive in (c for c in node.children if c.name == "directive"):
            dname = next(
                c.value for c in directive.children if c.name == "directive-name"
            ).lower()
            if dname == "max-age":
                dvalue = next(
                    (
                        c.value
                        for c in directive.children
                        if c.name == "directive-value"
                    ),
                    "0",
                )
                max_age = int(dvalue)
            elif dname == "includesubdomains":
                include_subdomains = True
            elif dname == "preload":
                preload = True
        return cls(max_age, include_subdomains, preload)

    @property
    def value(self) -> str:
        parts = [f"max-age={self.max_age}"]
        if self.include_subdomains:
            parts.append("includeSubDomains")
        if self.preload:
            parts.append("preload")
        return "; ".join(parts)
