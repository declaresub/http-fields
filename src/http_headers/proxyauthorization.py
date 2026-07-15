"""Proxy-Authorization header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.authbases import CredentialsHeader
from http_headers.visitors.rfc9110 import ProxyAuthorizationVisitor


class ProxyAuthorization(CredentialsHeader):
    """Proxy-Authorization header, as defined by RFC 9110."""

    name: ClassVar[str] = "proxy-authorization"
    rule: ClassVar[Rule] = rfc9110.Rule("Proxy-Authorization")
    visitor = ProxyAuthorizationVisitor()
