"""User-Agent header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.productlistheader import ProductListHeader
from http_headers.visitors.rfc9110 import UserAgentVisitor


class UserAgent(ProductListHeader):
    """User-Agent header, as defined by RFC 9110. ``items`` is a sequence of Product or
    Comment values."""

    name: ClassVar[str] = "User-Agent"
    rule: ClassVar[Rule] = rfc9110.Rule("User-Agent")
    visitor = UserAgentVisitor()
