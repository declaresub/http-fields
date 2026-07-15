from datetime import datetime
from typing import Any

from abnf import Node, NodeVisitor

from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9110 import (
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


class CacheDirective:
    def __init__(self, name: str, value: Any = True):

        self.name = Token(name)
        if name in ["max-age", "s-maxage", "max-stale", "min-fresh"]:
            self.value = NonNegativeInt(value)
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
            self.value = True
        elif name in ["no-cache", "private"]:
            if isinstance(value, str):
                # should consider parsing value to ensure it matches #field-name.
                self.value = QuotedString(value)
            else:
                self.value = True
        else:
            # extension (non-standard) directive: keep any value it carries.
            if isinstance(value, str):
                try:
                    self.value = Token(value)
                except ValueError:
                    self.value = QuotedString(value)
            else:
                self.value = True

    def __eq__(self, __o: object) -> bool:
        return (
            self.__dict__ == __o.__dict__
            if isinstance(__o, self.__class__)
            else NotImplemented
        )

    def __hash__(self) -> int:
        return hash((self.name, self.value))

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
