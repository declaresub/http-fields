"""LastModified header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.dateheader import DateHeader
from http_headers.visitors.rfc9110 import LastModifiedVisitor


class LastModified(DateHeader):
    """Last-Modified header, as defined by RFC 9110."""

    name: ClassVar[str] = "last-modified"
    rule: ClassVar[Rule] = rfc9110.Rule("Last-Modified")
    visitor = LastModifiedVisitor()
