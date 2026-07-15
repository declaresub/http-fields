"""Cache-Control header class."""

from dataclasses import dataclass
from typing import Any, ClassVar

from abnf import Rule
from abnf.grammars import rfc9111
from typing_extensions import Self

from http_headers.header import Header
from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9111 import CacheControlVisitor, CacheDirective

# directive-name -> field-name maps, shared by parse() and value.
_BOOL = {
    "immutable": "immutable",
    "public": "public",
    "no-store": "no_store",
    "no-transform": "no_transform",
    "must-revalidate": "must_revalidate",
    "proxy-revalidate": "proxy_revalidate",
    "only-if-cached": "only_if_cached",
}
_INT = {
    "max-age": "max_age",
    "max-stale": "max_stale",
    "min-fresh": "min_fresh",
    "s-maxage": "s_maxage",
}
_BOOL_OR_STR = {"no-cache": "no_cache", "private": "private"}


@dataclass(frozen=True, kw_only=True)
class CacheControl(Header):
    """Cache-Control header, as defined by RFC 9111.

    The ``no_cache`` and ``private`` directives may be ``True`` or a string of field names.
    Non-standard directives are carried in ``cache_extension``.
    """

    name: ClassVar[str] = "Cache-Control"
    rule: ClassVar[Rule] = rfc9111.Rule("Cache-Control")
    visitor: ClassVar[CacheControlVisitor] = CacheControlVisitor()

    immutable: bool = False
    public: bool = False
    private: bool | str = False
    no_cache: bool | str = False
    no_store: bool = False
    no_transform: bool = False
    must_revalidate: bool = False
    proxy_revalidate: bool = False
    max_age: int | None = None
    max_stale: int | None = None
    min_fresh: int | None = None
    only_if_cached: bool = False
    s_maxage: int | None = None
    cache_extension: tuple[CacheDirective, ...] = ()

    def __post_init__(self) -> None:
        # fail-fast coercion of the int-valued directives (frozen -> setattr).
        for attr in ("max_age", "max_stale", "min_fresh", "s_maxage"):
            v = getattr(self, attr)
            if v is not None:
                object.__setattr__(self, attr, NonNegativeInt(v))

    @classmethod
    def parse(cls, value: str) -> Self:
        kw: dict[str, Any] = {}
        extension: list[CacheDirective] = []
        for directive in cls.visitor.visit(cls._node(value)):
            n = str(directive.name)
            if n in _BOOL:
                kw[_BOOL[n]] = True
            elif n in _INT:
                kw[_INT[n]] = directive.value
            elif n in _BOOL_OR_STR:
                kw[_BOOL_OR_STR[n]] = (
                    directive.value if isinstance(directive.value, str) else True
                )
            else:
                extension.append(directive)
        return cls(**kw, cache_extension=tuple(extension))

    @property
    def value(self) -> str:
        out: list[CacheDirective] = []
        for n, attr in _BOOL.items():
            if getattr(self, attr):
                out.append(CacheDirective(n))
        for n, attr in _INT.items():
            v = getattr(self, attr)
            if v is not None:  # keep 0, unlike a truthiness check
                out.append(CacheDirective(n, v))
        for n, attr in _BOOL_OR_STR.items():
            v = getattr(self, attr)
            if isinstance(v, str):
                out.append(CacheDirective(n, v))
            elif v:
                out.append(CacheDirective(n))
        out.extend(self.cache_extension)
        return ",".join(str(directive) for directive in out)
