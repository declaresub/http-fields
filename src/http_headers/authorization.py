"""Authorization header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.authbases import CredentialsHeader
from http_headers.visitors.rfc9110 import (
    AuthorizationVisitor,
    AuthParamCredentials,
    TokenCredentials,
)

__all__ = ["AuthParamCredentials", "Authorization", "TokenCredentials"]


class Authorization(CredentialsHeader):
    """Authorization header, as defined by RFC 9110."""

    name: ClassVar[str] = "Authorization"
    rule: ClassVar[Rule] = rfc9110.Rule("Authorization")
    visitor = AuthorizationVisitor()
