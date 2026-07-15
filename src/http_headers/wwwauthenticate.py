"""WWW-Authenticate header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import (
    AuthParam,
    AuthParamChallenge,
    TokenChallenge,
    WWWAuthenticateVisitor,
)

__all__ = ["AuthParam", "AuthParamChallenge", "TokenChallenge", "WWWAuthenticate"]


@dataclass(frozen=True)
class WWWAuthenticate(Header):
    """WWW-Authenticate header, as defined by RFC 9110."""

    name: ClassVar[str] = "www-authenticate"
    rule: ClassVar[Rule] = rfc9110.Rule("WWW-Authenticate")
    visitor: ClassVar[WWWAuthenticateVisitor] = WWWAuthenticateVisitor()

    challenges: tuple[TokenChallenge | AuthParamChallenge, ...]

    def __init__(self, *challenges: TokenChallenge | AuthParamChallenge) -> None:
        object.__setattr__(self, "challenges", tuple(challenges))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(challenge) for challenge in self.challenges)
