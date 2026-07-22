"""Access-Control-* (CORS) header classes, as defined by the Fetch standard.

The grammar comes from abnf's ``cors`` module.
"""

from dataclasses import dataclass
from typing import ClassVar

from abnf import Rule
from abnf.grammars import cors
from typing_extensions import Self

from http_fields.header import Header
from http_fields.parsedobjs import NonNegativeInt, ParsedStr


class CorsMethod(ParsedStr):
    """A CORS method token. Self-validating."""

    parser = cors.Rule("method")


class CorsFieldName(ParsedStr):
    """A CORS field-name. Self-validating."""

    parser = cors.Rule("field-name")


class AllowedOrigin(ParsedStr):
    """An Access-Control-Allow-Origin value (an origin, ``null``, or ``*``). Self-validating."""

    parser = cors.Rule("Access-Control-Allow-Origin")


class RequestedMethod(ParsedStr):
    """An Access-Control-Request-Method value (a single method). Self-validating."""

    parser = cors.Rule("Access-Control-Request-Method")


__all__ = [
    "AccessControlAllowCredentials",
    "AccessControlAllowHeaders",
    "AccessControlAllowMethods",
    "AccessControlAllowOrigin",
    "AccessControlExposeHeaders",
    "AccessControlMaxAge",
    "AccessControlRequestHeaders",
    "AccessControlRequestMethod",
]


@dataclass(frozen=True)
class _CorsList(Header):
    """Base for CORS headers that are a comma-separated list of tokens (methods or
    field-names). Subclasses set ``name``/``rule`` and ``item_type`` (the self-validating
    ParsedStr type of each list item)."""

    item_type: ClassVar[type[ParsedStr]]

    # Subclasses narrow this to their item_type so the field-type check is strict.
    items: tuple[ParsedStr, ...]

    def __init__(self, *items: ParsedStr) -> None:
        object.__setattr__(self, "items", tuple(items))

    @classmethod
    def parse(cls, value: str) -> Self:
        node = cls._node(value)
        it = cls.item_type
        return cls(
            *(
                it(c.value, parse=False)
                for c in node.children
                if c.name == it.parser.name
            )
        )

    @property
    def value(self) -> str:
        return ", ".join(self.items)


class AccessControlAllowMethods(_CorsList):
    """Access-Control-Allow-Methods header."""

    name: ClassVar[str] = "access-control-allow-methods"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Allow-Methods")
    item_type = CorsMethod
    items: tuple[CorsMethod, ...]


class AccessControlAllowHeaders(_CorsList):
    """Access-Control-Allow-Headers header."""

    name: ClassVar[str] = "access-control-allow-headers"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Allow-Headers")
    item_type = CorsFieldName
    items: tuple[CorsFieldName, ...]


class AccessControlExposeHeaders(_CorsList):
    """Access-Control-Expose-Headers header."""

    name: ClassVar[str] = "access-control-expose-headers"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Expose-Headers")
    item_type = CorsFieldName
    items: tuple[CorsFieldName, ...]


class AccessControlRequestHeaders(_CorsList):
    """Access-Control-Request-Headers header."""

    name: ClassVar[str] = "access-control-request-headers"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Request-Headers")
    item_type = CorsFieldName
    items: tuple[CorsFieldName, ...]


@dataclass(frozen=True)
class AccessControlAllowOrigin(Header):
    """Access-Control-Allow-Origin header (an origin, ``null``, or ``*``)."""

    name: ClassVar[str] = "access-control-allow-origin"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Allow-Origin")

    origin: AllowedOrigin

    def __init__(self, origin: str) -> None:
        object.__setattr__(self, "origin", AllowedOrigin(origin))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    @property
    def value(self) -> str:
        return self.origin


@dataclass(frozen=True)
class AccessControlRequestMethod(Header):
    """Access-Control-Request-Method header (a single method)."""

    name: ClassVar[str] = "access-control-request-method"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Request-Method")

    method: RequestedMethod

    def __init__(self, method: str) -> None:
        object.__setattr__(self, "method", RequestedMethod(method))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    @property
    def value(self) -> str:
        return self.method


@dataclass(frozen=True)
class AccessControlMaxAge(Header):
    """Access-Control-Max-Age header (delta-seconds)."""

    name: ClassVar[str] = "access-control-max-age"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Max-Age")

    max_age: NonNegativeInt

    def __init__(self, max_age: int) -> None:
        object.__setattr__(self, "max_age", NonNegativeInt(max_age))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(NonNegativeInt(cls._node(value).value))

    @property
    def value(self) -> str:
        return str(self.max_age)


@dataclass(frozen=True)
class AccessControlAllowCredentials(Header):
    """Access-Control-Allow-Credentials header (always the literal ``true``)."""

    name: ClassVar[str] = "access-control-allow-credentials"
    rule: ClassVar[Rule] = cors.Rule("Access-Control-Allow-Credentials")

    @classmethod
    def parse(cls, value: str) -> Self:
        cls._node(value)  # validates the value is "true"
        return cls()

    @property
    def value(self) -> str:
        return "true"
