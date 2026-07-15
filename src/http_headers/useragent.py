"""User-Agent header class."""

from abnf import ParseError
from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import Comment, FieldName, Product, UserAgentVisitor


class UserAgent(Header):
    """User-Agent header.
    items attribute is a list of Product or Comment items.  Product
    has two attributes, product and product version."""

    name = FieldName("User-Agent")
    parse = rfc9110.Rule("User-Agent").parse_all
    visit = UserAgentVisitor().visit

    def __init__(self, value: str):
        """Intializes a User-Agent header.

        :param value: user-agent string.
        """

        self.value = value

    @property
    def value(self):
        """Returns header value."""
        # the grammar rule specifies at least one SP | TAB between itens.  Thus a
        # source string containing multiple spaces between items would not be reassembled
        # the same way.
        return " ".join(str(item) for item in self.items)

    @value.setter
    def value(self, val: str):
        try:
            node = self.parse(val)
        except ParseError as exc:
            raise ValueError(f"Invalid {self.name} value.") from exc
        self.items: list[Product | Comment] = self.visit(node)
