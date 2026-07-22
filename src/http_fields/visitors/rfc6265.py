from dataclasses import dataclass

from abnf import Node, NodeVisitor
from abnf.grammars import rfc6265

from http_fields.parsedobjs import ParsedStr


class CookieName(ParsedStr):
    """Represents an RFC 6265 cookie-name. Cookie names are case-sensitive."""

    parser = rfc6265.Rule("cookie-name")


class CookieValue(ParsedStr):
    """Represents a valid RFC 6265 cookie value."""

    parser = rfc6265.Rule("cookie-value")


@dataclass(frozen=True, slots=True)
class CookiePair:
    name: CookieName
    value: CookieValue

    def __init__(self, name: str, value: str) -> None:
        assert isinstance(name, str), "name must be str."
        assert isinstance(value, str), "value must be str."
        object.__setattr__(self, "name", CookieName(name))
        object.__setattr__(self, "value", CookieValue(value))


class CookieNameVisitor(NodeVisitor):
    @staticmethod
    def visit_cookie_name(node: Node) -> str:
        return CookieName(node.value, parse=False)


class CookieValueVisitor(NodeVisitor):
    @staticmethod
    def visit_cookie_value(node: Node):
        # Return the raw matched text so surrounding DQUOTEs (part of the value
        # per RFC 6265) are preserved, and an empty value stays "".
        return node.value


class CookiePairVisitor(NodeVisitor):
    visit_cookie_name = CookieNameVisitor()
    visit_cookie_value = CookieValueVisitor()

    def visit_cookie_pair(self, node: Node) -> CookiePair:
        # The "=" separator visits to None; an empty cookie-value visits to ""
        # (falsy but valid), so filter on identity, not truthiness.
        name, value = (v for v in map(self.visit, node.children) if v is not None)
        return CookiePair(name=name, value=value)


class CookieStringVisitor(NodeVisitor):
    visit_cookie_pair = CookiePairVisitor()

    def visit_cookie_string(self, node: Node) -> list[CookiePair]:
        return list(filter(None, map(self.visit, node.children)))
