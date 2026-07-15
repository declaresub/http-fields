"""Accept header class."""

from abnf.grammars import rfc9111

from http_headers.header import Header
from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9111 import AgeVisitor


class Age(Header):
    """Age header, as defined by RFC 9111."""

    name = "age"
    visitor = AgeVisitor()

    def __init__(self, value: str | None = None, seconds: int | None = None):
        if isinstance(value, str):
            self.value = value
        else:
            self.seconds = NonNegativeInt(seconds)

    @property
    def value(self):
        """Returns header value."""

        return str(self.seconds)

    @value.setter
    def value(self, val: str):
        rule = rfc9111.Rule("Age")
        node = rule.parse_all(val)
        self.seconds = self.visitor.visit(node)
