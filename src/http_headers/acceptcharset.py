"""Accept header class."""

from abnf.grammars import rfc9110

from http_headers.header import Header
from http_headers.visitors.rfc9110 import AcceptCharsetVisitor, Token, Weight


def _as_weight(value: float | Weight | None) -> Weight | None:
    """Normalize a weight argument to a Weight or None. A numeric 0 is a valid
    weight ("not acceptable"), so only None means "no weight specified"."""
    if isinstance(value, Weight):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return Weight(float(value))
    return None


class AcceptCharset(Header):
    """Accept-Charset header, as defined by RFC 9110."""

    name = "accept-charset"
    visitor = AcceptCharsetVisitor()

    def __init__(
        self,
        value: str | None = None,
        charsets: list[tuple[str, float | Weight | None]] | None = None,
    ):
        if isinstance(value, str):
            self.value = value
        else:
            self.charsets = (
                [(Token(c), _as_weight(w)) for c, w in charsets] if charsets else []
            )

    @property
    def value(self):
        """Returns header value."""

        x = [
            charset + (";" + str(weight)) if weight else ""
            for charset, weight in self.charsets
        ]
        return ", ".join(x)

    @value.setter
    def value(self, val: str):
        rule = rfc9110.Rule("Accept-Charset")
        node = rule.parse_all(val)
        self.charsets: list[tuple[Token, Weight | None]] = self.visitor.visit(node)
