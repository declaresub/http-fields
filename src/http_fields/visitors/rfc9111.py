from dataclasses import dataclass
from datetime import datetime
from typing import Any

from abnf import Node, NodeVisitor

from http_fields.parsedobjs import NonNegativeInt
from http_fields.visitors.rfc9110 import (
    HttpDateVisitor,
    QuotedString,
    QuotedStringVisitor,
    Token,
    TokenVisitor,
)


class AgeVisitor(NodeVisitor):
    @staticmethod
    def visit_age(node: Node):
        return NonNegativeInt(node.value)


@dataclass(frozen=True)
class CacheDirective:
    name: Token
    value: Any = True

    def __init__(self, name: str, value: Any = True) -> None:
        object.__setattr__(self, "name", Token(name))
        resolved: Any
        if name == "max-stale":
            # RFC 9111 section 5.2.1.2: max-stale may be used with no value,
            # meaning "stale responses of any age".
            resolved = True if value is None or value is True else NonNegativeInt(value)
        elif name in ["max-age", "s-maxage", "min-fresh"]:
            if value is None:
                raise ValueError(f"Cache directive '{name}' requires a value.")
            resolved = NonNegativeInt(value)
        elif name in [
            "immutable",
            "must-revalidate",
            "must-understand",
            "no-store",
            "no-transform",
            "only-if-cached",
            "proxy-revalidate",
            "public",
        ]:
            # immutable is defined in RFC 8246, a proposed standard.  But the directive appears to be in use.
            resolved = True
        elif name in ["no-cache", "private"]:
            # should consider parsing value to ensure it matches #field-name.
            resolved = QuotedString(value) if isinstance(value, str) else True
        else:
            # extension (non-standard) directive: keep any value it carries.
            if isinstance(value, str):
                try:
                    resolved = Token(value)
                except ValueError:
                    resolved = QuotedString(value)
            else:
                resolved = True
        object.__setattr__(self, "value", resolved)

    def __str__(self):
        return str(self.name) if self.value is True else f"{self.name}={self.value}"


class CacheDirectiveVisitor(NodeVisitor):
    visit_quoted_string = QuotedStringVisitor()
    visit_token = TokenVisitor()

    def visit_cache_directive(self, node: Node) -> CacheDirective:
        items = filter(None, map(self.visit, node.children))
        name = next(items)
        value = next(items, None)
        return CacheDirective(name, value)


class CacheControlVisitor(NodeVisitor):
    visit_cache_directive = CacheDirectiveVisitor()

    def visit_cache_control(self, node: Node) -> list[CacheDirective]:
        directives = list(filter(None, map(self.visit, node.children)))
        return directives


class ExpiresVisitor(NodeVisitor):
    visit_http_date = HttpDateVisitor()

    def visit_expires(self, node: Node) -> datetime:
        return next(filter(None, map(self.visit, node.children)))
