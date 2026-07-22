"""Allow header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import ParsedStr
from http_fields.visitors.rfc9110 import AllowVisitor


class Method(ParsedStr):
    """An HTTP method (a token). Methods are case-sensitive (RFC 9110 section 9.1),
    unlike the caseless :class:`Token`."""

    parser = rfc9110.Rule("token")


@dataclass(frozen=True)
class Allow(Header):
    """Allow header, as defined by RFC 9110.

    Allow: GET, POST, OPTIONS
    """

    name: ClassVar[str] = "Allow"
    rule: ClassVar[Rule] = rfc9110.Rule("Allow")
    visitor: ClassVar[AllowVisitor] = AllowVisitor()

    methods: tuple[Method, ...]

    def __init__(self, *methods: Method) -> None:
        object.__setattr__(self, "methods", tuple(methods))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(
            *(Method(m, parse=False) for m in cls.visitor.visit(cls._node(value)))
        )

    @property
    def value(self) -> str:
        return ",".join(self.methods)
