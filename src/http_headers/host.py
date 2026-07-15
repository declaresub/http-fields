"""Host header class"""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import HostVisitor


class Host(Header):  # pylint: disable=too-few-public-methods
    """
    Host header.
    Host: www.example.com
    """

    name = "host"
    visitor = HostVisitor()

    def __init__(self, value: str):
        """
        :param hostname: a hostname.
        :param value: raw header value
        :rvalue: None
        :raises ValueError:
        """

        self.value = value

    @property
    def value(self):
        return self.hostname + (f":{self.port}" if self.port else "")

    @value.setter
    def value(self, val: str):
        node = rfc9110.Rule("Host").parse_all(val)
        self.hostname, self.port = self.visitor.visit(node)
