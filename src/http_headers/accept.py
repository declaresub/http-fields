"""Accept header class."""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AcceptType, AcceptVisitor, FieldName


class Accept(Header):
    """Accept header, as defined by RFC 9110.

    Note that an Accept header may have empty value; that is, 'Accept: ' is valid according to RFC 9110.  So are
    'Accept: ,'. 'Accept: ', text/html', etc.  An Accept header with empty value should be treated as acceptance
    of any media type.

    Also note that the Accept header definition in RFC 9110 no longer includes ext-params (accept-ext in the grammar)."""

    name = FieldName("Accept")
    visitor = AcceptVisitor()

    def __init__(
        self,
        value: str | None = None,
        *,
        accept_types: list[AcceptType] | None = None,
    ):
        if isinstance(value, str):
            self.value = value
        else:
            self.accept_types = list(accept_types) if accept_types else []

    @property
    def value(self):
        """Returns header value."""
        return ", ".join(str(accept_type) for accept_type in self.accept_types)

    @value.setter
    def value(self, val: str):
        rule = rfc9110.Rule("Accept")
        node = rule.parse_all(val)
        self.accept_types: list[AcceptType] = self.visitor.visit(node)
