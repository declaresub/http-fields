"""LastModified header class."""

from datetime import datetime

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import LastModifiedVisitor, imf_fixdate


class LastModified(Header):
    """Last-Modified header, as defined by RFC 9110."""

    name = "last-modified"
    visitor = LastModifiedVisitor()

    def __init__(self, value: str | datetime):
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, datetime):  # type: ignore
            self.date = value
        else:
            raise TypeError("value must be a str or datetime.")

    @property
    def value(self):
        """Returns header value."""

        return imf_fixdate(self.date)

    @value.setter
    def value(self, val: str):
        rule = rfc9110.Rule("Last-Modified")
        node = rule.parse_all(val)
        self.date = self.visitor.visit(node)
