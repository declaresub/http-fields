"""WWW-Authenticate header class."""

from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110

from http_headers.authbases import ChallengeListHeader
from http_headers.visitors.rfc9110 import (
    AuthParam,
    AuthParamChallenge,
    TokenChallenge,
    WWWAuthenticateVisitor,
)

__all__ = ["AuthParam", "AuthParamChallenge", "TokenChallenge", "WWWAuthenticate"]


class WWWAuthenticate(ChallengeListHeader):
    """WWW-Authenticate header, as defined by RFC 9110."""

    name: ClassVar[str] = "www-authenticate"
    rule: ClassVar[Rule] = rfc9110.Rule("WWW-Authenticate")
    visitor = WWWAuthenticateVisitor()
