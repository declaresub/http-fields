"""Content-Type header class."""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import rfc9110
from typing_extensions import Self

from http_headers.header import Header
from http_headers.visitors.rfc9110 import ContentTypeVisitor, MediaType, Parameter
from http_headers.visitors.rfc9110.quotedstring import QuotedString


def _unquote(value: str) -> str:
    """Return the logical value of a parameter, stripping the surrounding DQUOTEs
    and unescaping quoted-pairs when it is a quoted-string."""
    if not isinstance(value, QuotedString):
        return str(value)
    inner = str(value)[1:-1]
    out: list[str] = []
    i = 0
    while i < len(inner):
        if inner[i] == "\\" and i + 1 < len(inner):
            out.append(inner[i + 1])
            i += 2
        else:
            out.append(inner[i])
            i += 1
    return "".join(out)


@dataclass(frozen=True)
class ContentType(Header):
    """Content-Type header, as defined by RFC 9110."""

    name: ClassVar[str] = "Content-Type"
    rule: ClassVar[Rule] = rfc9110.Rule("Content-Type")
    visitor: ClassVar[ContentTypeVisitor] = ContentTypeVisitor()

    media_type: MediaType

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(cls.visitor.visit(cls._node(value)))

    @classmethod
    def of(
        cls,
        type: str,
        subtype: str,
        *,
        charset: str | None = None,
        boundary: str | None = None,
        params: list[tuple[str, str]] | None = None,
    ) -> Self:
        """Build a Content-Type from its pieces. ``charset``/``boundary`` take precedence
        over any same-named entry in ``params``."""
        all_params: list[Parameter] = [
            p
            for p in (
                Parameter("charset", charset) if charset else None,
                Parameter("boundary", boundary) if boundary else None,
            )
            if p is not None
        ]
        for name, val in params or []:
            param = Parameter(name, val)
            if (param.name == "charset" and charset) or (
                param.name == "boundary" and boundary
            ):
                continue
            all_params.append(param)
        return cls(MediaType(type, subtype, all_params))

    @property
    def type(self) -> str:
        return self.media_type.type

    @property
    def subtype(self) -> str:
        return self.media_type.subtype

    @property
    def params(self) -> list[Parameter]:
        return list(self.media_type.params)

    @property
    def charset(self) -> str | None:
        for param in self.media_type.params:
            if param.name == "charset":
                return _unquote(param.value)
        return None

    @property
    def boundary(self) -> str | None:
        for param in self.media_type.params:
            if param.name == "boundary":
                return _unquote(param.value)
        return None

    @property
    def value(self) -> str:
        return str(self.media_type)
