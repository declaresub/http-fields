"""Expires header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9111

from http_fields.dateheader import DateHeader
from http_fields.visitors.rfc9111 import ExpiresVisitor


class Expires(DateHeader):
    """Expires header, as defined by RFC 9111."""

    name: ClassVar[str] = "expires"
    rule: ClassVar[Rule] = rfc9111.Rule("Expires")
    visitor = ExpiresVisitor()
