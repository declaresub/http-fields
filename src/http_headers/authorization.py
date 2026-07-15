"""Authorization header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import (
    AuthorizationVisitor,
    AuthParamCredentials,
    TokenCredentials,
)

__all__ = ["AuthParamCredentials", "Authorization", "TokenCredentials"]


@dataclass(frozen=True)
class Authorization(Header):
    """Authorization header, as defined by RFC 9110."""

    name: ClassVar[str] = "Authorization"
    rule: ClassVar[Rule] = rfc9110.Rule("Authorization")
    visitor: ClassVar[AuthorizationVisitor] = AuthorizationVisitor()

    credentials: TokenCredentials | AuthParamCredentials

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return str(self.credentials)
