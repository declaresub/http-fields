from datetime import datetime

from abnf.grammars import rfc9111

from http_headers.header import Header
from http_headers.visitors.rfc9110 import imf_fixdate
from http_headers.visitors.rfc9111 import ExpiresVisitor


class Expires(Header):
    """Expires header, as defined by RFC 9111."""

    name = "expires"
    visitor = ExpiresVisitor()

    def __init__(self, value: str | datetime):
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, datetime):  # type: ignore
            self.expire_date = value
        else:
            raise TypeError("expire_date must be str or datetime.")

    @property
    def value(self):
        """Returns header value."""

        return imf_fixdate(self.expire_date)

    @value.setter
    def value(self, val: str):
        rule = rfc9111.Rule("Expires")
        node = rule.parse_all(val)
        self.expire_date = self.visitor.visit(node)
