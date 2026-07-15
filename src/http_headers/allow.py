"""Allow header class"""

from abnf import ParseError
from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AllowVisitor, Token


class Allow(Header):
    """
    Allow header.
    Allow: GET, POST, OPTIONS
    """

    name = "Allow"
    visitor = AllowVisitor()

    def __init__(self, value: str | None = None, *, methods: list[str] | None = None):
        """
        :param methods: a list of method names.
        :rvalue: None
        """
        if isinstance(value, str):
            self.value = value
        else:
            self.methods = [Token(m) for m in methods] if methods else []

    @property
    def value(self):
        """Returns header value."""
        return ",".join(self.methods)

    @value.setter
    def value(self, val: str):
        try:
            node = rfc9110.Rule("Allow").parse_all(val)
        except ParseError as exc:
            raise ValueError(f'Invalid Allow header value "{val}".') from exc

        self.methods: list[Token] = self.visitor.visit(node)
