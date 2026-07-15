from abnf import ParseError
from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import ConnectionVisitor, Token


class Connection(Header):
    name = "connection"
    visitor = ConnectionVisitor()

    def __init__(self, *value: str):
        """Pass connection directives as a single header value string, or a list of string."""

        assert isinstance(value, tuple)
        if len(value) == 1:
            self.value = value[0]
        else:
            self.directives = [Token(v) for v in value]

    @property
    def value(self):
        return ",".join(self.directives)

    @value.setter
    def value(self, val: str):
        try:
            node = rfc9110.Rule("Connection").parse_all(val)
        except ParseError as exc:
            raise ValueError(f'Invalid {self.name} header value "{val}".') from exc
        else:
            self.directives: list[Token] = self.visitor.visit(node)
