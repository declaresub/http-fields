from abnf import Node, NodeVisitor
from abnf.grammars import rfc6265

from http_headers.parsedobjs import CaselessMixin, ParsedStr


class CookieName(CaselessMixin, ParsedStr):
    """Represents an RFC 6265 cookie-name."""

    parser = rfc6265.Rule("cookie-name")


class CookieValue(ParsedStr):
    """Represents a valid RFC 6265 cookie value."""

    parser = rfc6265.Rule("cookie-value")


class CookiePair:
    __slots__ = ("name", "value", "_key")

    def __init__(self, name: str, value: str):
        assert isinstance(name, str), "name must be str."
        assert isinstance(value, str), "value must be str."
        self.name = CookieName(name)
        self.value = CookieValue(value)
        self._key = (self.name, self.value)

    def __eq__(self, __x: object) -> bool:
        return (
            self._key == __x._key if isinstance(__x, self.__class__) else NotImplemented
        )

    def __hash__(self):
        return hash(self._key)


class CookieNameVisitor(NodeVisitor):
    @staticmethod
    def visit_cookie_name(node: Node) -> str:
        return CookieName(node.value, parse=False)


class CookieValueVisitor(NodeVisitor):
    def visit_cookie_value(self, node: Node):
        return "".join(filter(None, map(self.visit, node.children)))

    @staticmethod
    def visit_cookie_octet(node: Node):
        return node.value


class CookiePairVisitor(NodeVisitor):
    visit_cookie_name = CookieNameVisitor()
    visit_cookie_value = CookieValueVisitor()

    def visit_cookie_pair(self, node: Node) -> CookiePair:
        name, value = filter(None, map(self.visit, node.children))
        return CookiePair(name=name, value=value)


class CookieStringVisitor(NodeVisitor):
    visit_cookie_pair = CookiePairVisitor()

    def visit_cookie_string(self, node: Node) -> list[CookiePair]:
        return list(filter(None, map(self.visit, node.children)))
