"""Server header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_fields.productlistheader import ProductListHeader
from http_fields.visitors.rfc9110 import ServerVisitor


class Server(ProductListHeader):
    """Server header, as defined by RFC 9110. ``items`` is a sequence of Product or
    Comment values."""

    name: ClassVar[str] = "Server"
    rule: ClassVar[Rule] = rfc9110.Rule("Server")
    visitor = ServerVisitor()
