"""Cookie header class."""

from abnf.grammars import rfc6265

from http_headers.header import Header
from http_headers.visitors.rfc6265 import CookiePair, CookieStringVisitor


class Cookie(Header):
    """Cookie header."""

    name = "Cookie"
    visitor = CookieStringVisitor()

    def __init__(self, value: str | list[tuple[str, str]]):

        if isinstance(value, str):
            self.value = value
        elif isinstance(value, list):  # type: ignore
            self.pairs = [CookiePair(*t) for t in value]
        else:
            raise TypeError("value must be str or list[tuple[str, str]].")

    @property
    def value(self) -> str:
        return "; ".join(f"{pair.name}={pair.value}" for pair in self.pairs)

    @value.setter
    def value(self, val: str):
        rule = rfc6265.Rule("cookie-string")
        # apparently cookies are often sent with a trailing semicolon, thus rendering them
        # invalid.  So we remove them before parsing.
        val = val.rstrip(";")
        node = rule.parse_all(val)
        self.pairs: list[CookiePair] = self.visitor.visit(node)
