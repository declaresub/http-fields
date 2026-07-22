"""Authorization header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_fields.authbases import CredentialsHeader
from http_fields.visitors.rfc9110 import (
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
