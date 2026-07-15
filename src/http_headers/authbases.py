"""Base classes for the authentication / authorization header families.

These pair a request/response header with its proxy counterpart:
``ChallengeListHeader`` (WWW-Authenticate / Proxy-Authenticate), ``CredentialsHeader``
(Authorization / Proxy-Authorization), and ``AuthParamsHeader`` (Authentication-Info /
Proxy-Authentication-Info). Concrete subclasses supply ``name``/``rule``/``visitor``.
"""

from dataclasses import dataclass
from typing import ClassVar

from abnf import NodeVisitor
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import (
    AuthParam,
    AuthParamChallenge,
    AuthParamCredentials,
    TokenChallenge,
    TokenCredentials,
)


@dataclass(frozen=True)
class ChallengeListHeader(Header):
    """Base for headers that are a list of authentication challenges."""

    visitor: ClassVar[NodeVisitor]

    challenges: tuple[TokenChallenge | AuthParamChallenge, ...]

    def __init__(self, *challenges: TokenChallenge | AuthParamChallenge) -> None:
        object.__setattr__(self, "challenges", tuple(challenges))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ", ".join(str(challenge) for challenge in self.challenges)


@dataclass(frozen=True)
class CredentialsHeader(Header):
    """Base for headers carrying a single credentials value."""

    visitor: ClassVar[NodeVisitor]

    credentials: TokenCredentials | AuthParamCredentials

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return str(self.credentials)


@dataclass(frozen=True)
class AuthParamsHeader(Header):
    """Base for headers that are a list of auth-params."""

    visitor: ClassVar[NodeVisitor]

    auth_params: tuple[AuthParam, ...] = ()

    def __init__(self, *auth_params: AuthParam) -> None:
        object.__setattr__(self, "auth_params", tuple(auth_params))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ",".join(str(p) for p in self.auth_params)
