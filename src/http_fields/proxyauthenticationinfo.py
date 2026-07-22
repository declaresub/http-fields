"""Proxy-Authentication-Info header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_fields.authbases import AuthParamsHeader
from http_fields.visitors.rfc9110 import ProxyAuthenticationInfoVisitor


class ProxyAuthenticationInfo(AuthParamsHeader):
    """Proxy-Authentication-Info header, as defined by RFC 9110."""

    name: ClassVar[str] = "proxy-authentication-info"
    rule: ClassVar[Rule] = rfc9110.Rule("Proxy-Authentication-Info")
    visitor = ProxyAuthenticationInfoVisitor()
