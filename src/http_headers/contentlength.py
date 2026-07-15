"""ContentLength header class"""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9110 import ContentLengthVisitor, FieldName


class ContentLength(Header):
    """Content-Length header."""

    name = FieldName("content-length")
    visitor = ContentLengthVisitor()

    def __init__(self, value: str | int):
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, int):  # type: ignore
            self.length = NonNegativeInt(value)
        else:
            raise TypeError("value must either be str or int.")

    @property
    def value(self):
        return str(self.length)

    @value.setter
    def value(self, val: str):
        node = rfc9110.Rule("Content-Length").parse_all(val)
        self.length = self.visitor.visit(node)
