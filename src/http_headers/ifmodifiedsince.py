"""IfModifiedSince header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.dateheader import DateHeader
from http_headers.visitors.rfc9110 import IfModifiedSinceVisitor


class IfModifiedSince(DateHeader):
    """If-Modified-Since header, as defined by RFC 9110."""

    name: ClassVar[str] = "If-Modified-Since"
    rule: ClassVar[Rule] = rfc9110.Rule("If-Modified-Since")
    visitor = IfModifiedSinceVisitor()
