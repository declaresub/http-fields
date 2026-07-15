"""Authentication-Info header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AuthenticationInfoVisitor, AuthParam


@dataclass(frozen=True)
class AuthenticationInfo(Header):
    """Authentication-Info header, as defined by RFC 9110."""

    name: ClassVar[str] = "authentication-info"
    rule: ClassVar[Rule] = rfc9110.Rule("Authentication-Info")
    visitor: ClassVar[AuthenticationInfoVisitor] = AuthenticationInfoVisitor()

    auth_params: tuple[AuthParam, ...] = ()

    def __init__(self, *auth_params: AuthParam) -> None:
        object.__setattr__(self, "auth_params", tuple(auth_params))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(*cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return ",".join(str(p) for p in self.auth_params)
