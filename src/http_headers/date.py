from datetime import datetime

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import DateVisitor, imf_fixdate


class Date(Header):
    """Date header, as defined by RFC 9110."""

    name = "date"
    visitor = DateVisitor()

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
        rule = rfc9110.Rule("Date")
        node = rule.parse_all(val)
        self.date = self.visitor.visit(node)
