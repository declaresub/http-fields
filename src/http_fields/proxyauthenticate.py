"""Proxy-Authenticate header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_fields.authbases import ChallengeListHeader
from http_fields.visitors.rfc9110 import ProxyAuthenticateVisitor


class ProxyAuthenticate(ChallengeListHeader):
    """Proxy-Authenticate header, as defined by RFC 9110."""

    name: ClassVar[str] = "proxy-authenticate"
    rule: ClassVar[Rule] = rfc9110.Rule("Proxy-Authenticate")
    visitor = ProxyAuthenticateVisitor()
