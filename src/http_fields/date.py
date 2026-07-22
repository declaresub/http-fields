"""Date header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_fields.dateheader import DateHeader
from http_fields.visitors.rfc9110 import DateVisitor


class Date(DateHeader):
    """Date header, as defined by RFC 9110."""

    name: ClassVar[str] = "date"
    rule: ClassVar[Rule] = rfc9110.Rule("Date")
    visitor = DateVisitor()
