"""Authorization header class"""

from abnf import ParseError
from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import (
    AuthorizationVisitor,
    AuthParamCredentials,
    FieldName,
    TokenCredentials,
)


class Authorization(Header):
    """Authorization header."""

    name = FieldName("Authorization")

    def __init__(
        self,
        value: str | None = None,
        *,
        credentials: TokenCredentials | AuthParamCredentials | None = None,
    ):

        if isinstance(value, str):
            self.value = value
        else:
            if not credentials:
                raise ValueError("Either value or credentials must be supplied.")
            self.credentials = credentials

    @property
    def value(self):
        return str(self.credentials)

    @value.setter
    def value(self, val: str):
        try:
            node = rfc9110.Rule("Authorization").parse_all(val)
        except ParseError as exc:
            raise ValueError(f'Invalid {self.name} value "{val}".') from exc
        else:
            visitor = AuthorizationVisitor()
            self.credentials = visitor.visit(node)
