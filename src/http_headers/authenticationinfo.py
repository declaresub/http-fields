"""Authentication-Info header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.authbases import AuthParamsHeader
from http_headers.visitors.rfc9110 import AuthenticationInfoVisitor, AuthParam

__all__ = ["AuthenticationInfo", "AuthParam"]


class AuthenticationInfo(AuthParamsHeader):
    """Authentication-Info header, as defined by RFC 9110."""

    name: ClassVar[str] = "authentication-info"
    rule: ClassVar[Rule] = rfc9110.Rule("Authentication-Info")
    visitor = AuthenticationInfoVisitor()
