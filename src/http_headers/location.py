"""Location header class."""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import LocationVisitor


class Location(Header):
    """Location header"""

    name = "Location"
    visitor = LocationVisitor()

    def __init__(self, value: str):
        """Initializes Location header.  Pass a value with url to set the uri value of
        the header.

        :param value:
        :param url:
        :returns None:
        """

        assert isinstance(value, str)
        self.value = value

    @property
    def value(self) -> str:
        return self.uri

    @value.setter
    def value(self, val: str):
        node = rfc9110.Rule("Location").parse_all(val)
        self.uri: str = self.visitor.visit(node)
