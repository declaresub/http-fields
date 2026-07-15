"""Allow header class"""

from abnf import ParseError
from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AuthenticationInfoVisitor, AuthParam


class AuthenticationInfo(Header):
    name = "authentication-info"
    visitor = AuthenticationInfoVisitor()

    def __init__(
        self,
        value: str | None = None,
        *,
        auth_params: list[AuthParam] | None = None,
    ):
        if isinstance(value, str):
            self.value = value
        else:
            self.auth_params = list(auth_params) if auth_params else []

    @property
    def value(self):
        """Returns header value."""
        return ",".join(str(p) for p in self.auth_params)

    @value.setter
    def value(self, val: str):
        try:
            node = rfc9110.Rule("Authentication-Info").parse_all(val)
        except ParseError as exc:
            raise ValueError(f'Invalid {self.name} header value "{val}".') from exc
        else:
            self.auth_params: list[AuthParam] = self.visitor.visit(node)
